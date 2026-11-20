from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, connection, transaction
from django.test import TransactionTestCase
from django.utils import timezone

from .models import (
    AuditLog, Bundle, BundleItem, BundlePurchaseSnapshot, Course, Entitlement,
    EntitlementGrant, Order, OrderItem, Pattern, PatternFile, PatternRelease,
    PatternVariant, PaymentAttempt, Product, ProductPrice, Promotion, PromotionProduct, Refund, RefundItem,
    Review, User,
)
from .services import complete_refund, grant_manual, grant_purchase, snapshot_bundle


class IntegrityTests(TransactionTestCase):
    def setUp(self):
        with transaction.atomic():
            self.student = User.objects.create_user('+989000009001', 'fictional-test-password')
            self.other = User.objects.create_user('+989000009002', 'other-fictional-password')
            self.admin = User.objects.create_superuser('+989000009003', 'admin-fictional-password')
            self.product = Product.objects.create(slug='course', title='دوره', kind='course')
            Course.objects.create(product=self.product)

    def purchase(self, product=None):
        product = product or self.product
        with transaction.atomic():
            order = Order.objects.create(order_number=f'TEST-{Order.objects.count()}',user=self.student,subtotal=100,payable_total=100)
            item = OrderItem.objects.create(order=order,product=product,product_title=product.title,product_kind=product.kind,unit_price=100,final_amount=100)
            if product.kind=='bundle':
                snapshot_bundle(item)
            payment = PaymentAttempt.objects.create(order=order,provider='mock',amount=100,status='succeeded',verified_at=timezone.now(),idempotency_key=f'TEST-{order.pk}')
            order.status='paid'
            order.paid_at=timezone.now()
            order.save()
            grant_purchase(item)
        return order,item,payment

    def test_price_overlap_and_adjacent_intervals(self):
        start=timezone.now()
        ProductPrice.objects.create(product=self.product,amount=100,valid_from=start,valid_until=start+timedelta(days=1))
        ProductPrice.objects.create(product=self.product,amount=120,valid_from=start+timedelta(days=1))
        with self.assertRaises(IntegrityError), transaction.atomic():
            ProductPrice.objects.create(product=self.product,amount=90,valid_from=start+timedelta(hours=1))

    def test_financial_snapshots_and_captured_payment_are_immutable(self):
        order,item,payment=self.purchase()
        for model,pk,changes in [(Order,order.pk,{'subtotal':200}),(OrderItem,item.pk,{'product_title':'changed'}),(PaymentAttempt,payment.pk,{'status':'failed'})]:
            with self.assertRaises(IntegrityError), transaction.atomic():
                model.objects.filter(pk=pk).update(**changes)

    def test_order_sum_and_status_transition(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Order.objects.create(order_number='BAD',user=self.student,subtotal=100,payable_total=100)
        order=Order.objects.create(order_number='EMPTY',user=self.student,subtotal=0,payable_total=0,status='cancelled')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Order.objects.filter(pk=order.pk).update(status='pending')

    def test_cross_pattern_file_and_null_variant_uniqueness(self):
        with transaction.atomic():
            p1=Product.objects.create(slug='p1',title='الگو یک',kind='pattern')
            pattern1=Pattern.objects.create(product=p1)
            p2=Product.objects.create(slug='p2',title='الگو دو',kind='pattern')
            pattern2=Pattern.objects.create(product=p2)
            release=PatternRelease.objects.create(pattern=pattern1,version='1')
            variant=PatternVariant.objects.create(pattern=pattern2,size_label='M')
        values={'release':release,'pattern':pattern1,'file_kind':'a4','storage_key':'placeholder','checksum_sha256':'a'*64,'size_bytes':1,'display_name':'test'}
        with self.assertRaises(IntegrityError), transaction.atomic():
            PatternFile.objects.create(variant=variant,**values)
        PatternFile.objects.create(variant=None,**values)
        with self.assertRaises(IntegrityError), transaction.atomic():
            PatternFile.objects.create(variant=None,**values)

    def test_purchaser_review_and_rating(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(user=self.student,product=self.product,rating=5)
        self.purchase()
        Review.objects.create(user=self.student,product=self.product,rating=5,status='approved')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(user=self.other,product=self.product,rating=6)

    def test_bundle_snapshot_survives_composition_change(self):
        with transaction.atomic():
            product=Product.objects.create(slug='bundle',title='بسته',kind='bundle')
            bundle=Bundle.objects.create(product=product)
            component=BundleItem.objects.create(bundle=bundle,product=self.product,position=0)
        order,item,payment=self.purchase(product)
        component.delete()
        self.assertTrue(Entitlement.objects.filter(user=self.student,product=self.product,status='active').exists())
        snapshot=BundlePurchaseSnapshot.objects.get(order_item=item)
        with self.assertRaises(IntegrityError), transaction.atomic():
            BundlePurchaseSnapshot.objects.filter(pk=snapshot.pk).update(product_title='changed')
        with self.assertRaises(IntegrityError), transaction.atomic():
            BundleItem.objects.create(bundle=bundle,product=product,position=0)

    def test_refund_preserves_independent_manual_grant(self):
        order,item,payment=self.purchase()
        grant_manual(actor=self.admin,user=self.student,product=self.product,reason='بورسیه مستقل')
        with transaction.atomic():
            refund=Refund.objects.create(payment=payment,amount=100,status='approved')
            RefundItem.objects.create(refund=refund,order_item=item,amount=100)
        complete_refund(refund_id=refund.pk,actor=self.admin,provider_ref='mock-refund')
        self.assertEqual(EntitlementGrant.objects.get(order_item=item).status,'revoked')
        self.assertEqual(Entitlement.objects.get(user=self.student,product=self.product).status,'active')
        with connection.cursor() as cursor:
            cursor.execute('SELECT sales_amount,refunded_amount,net_sales_amount FROM daily_sales')
            self.assertEqual(cursor.fetchone(),(Decimal(100),Decimal(100),Decimal(0)))

    def test_refund_cannot_exceed_capture(self):
        order,item,payment=self.purchase()
        with self.assertRaises(IntegrityError), transaction.atomic():
            refund=Refund.objects.create(payment=payment,amount=101)
            RefundItem.objects.create(refund=refund,order_item=item,amount=101)

    def test_manual_grant_permissions_and_append_only_audit(self):
        with self.assertRaises(PermissionDenied):
            grant_manual(actor=self.student,user=self.student,product=self.product,reason='not authorized')
        grant_manual(actor=self.admin,user=self.student,product=self.product,reason='دسترسی آزمایشی')
        with self.assertRaises(IntegrityError), transaction.atomic():
            AuditLog.objects.all().update(action='tampered')

    def test_duplicate_capture_is_visible_without_sales_double_count(self):
        order,item,payment=self.purchase()
        PaymentAttempt.objects.create(order=order,provider='mock',amount=100,status='succeeded',verified_at=timezone.now(),idempotency_key='duplicate-charge')
        with connection.cursor() as cursor:
            cursor.execute('SELECT sales_amount,captured_amount,net_cash_amount FROM daily_sales')
            self.assertEqual(cursor.fetchone(),(Decimal(100),Decimal(200),Decimal(200)))

    def test_fixed_discount_cannot_exceed_applicable_price(self):
        now = timezone.now()
        ProductPrice.objects.create(product=self.product,amount=100,valid_from=now)
        promotion = Promotion.objects.create(name='test',discount_type='fixed',value=101,starts_at=now,ends_at=now+timedelta(days=1))
        with self.assertRaises(IntegrityError), transaction.atomic():
            PromotionProduct.objects.create(promotion=promotion,product=self.product)

    def test_paid_direct_purchase_requires_grant(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            order=Order.objects.create(order_number='NO-GRANT',user=self.student,subtotal=100,payable_total=100)
            OrderItem.objects.create(order=order,product=self.product,product_title=self.product.title,product_kind='course',unit_price=100,final_amount=100)
            PaymentAttempt.objects.create(order=order,provider='mock',amount=100,status='succeeded',verified_at=timezone.now(),idempotency_key='no-grant')
            order.status='paid'
            order.paid_at=timezone.now()
            order.save()

    def test_partial_refund_preserves_purchase_access(self):
        order,item,payment=self.purchase()
        with transaction.atomic():
            refund=Refund.objects.create(payment=payment,amount=40,status='approved')
            RefundItem.objects.create(refund=refund,order_item=item,amount=40)
        complete_refund(refund_id=refund.pk,actor=self.admin,provider_ref='partial-mock')
        self.assertEqual(EntitlementGrant.objects.get(order_item=item).status,'active')
        self.assertEqual(Entitlement.objects.get(user=self.student,product=self.product).status,'active')

    def test_full_refund_revokes_access_without_independent_grant(self):
        order,item,payment=self.purchase()
        with transaction.atomic():
            refund=Refund.objects.create(payment=payment,amount=100,status='approved')
            RefundItem.objects.create(refund=refund,order_item=item,amount=100)
        complete_refund(refund_id=refund.pk,actor=self.admin,provider_ref='full-mock')
        self.assertEqual(EntitlementGrant.objects.get(order_item=item).status,'revoked')
        self.assertEqual(Entitlement.objects.get(user=self.student,product=self.product).status,'revoked')
