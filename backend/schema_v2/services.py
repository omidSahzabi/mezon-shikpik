"""Transactional database operations, intentionally without API endpoints."""
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    AuditLog, BundleItem, BundlePurchaseSnapshot, Entitlement, EntitlementEvent,
    EntitlementGrant, Order, OrderItem, Refund, RefundItem,
)


@transaction.atomic
def snapshot_bundle(item):
    order = Order.objects.select_for_update().get(pk=item.order_id)
    if order.status != 'pending' or item.product_kind != 'bundle':
        raise ValidationError('Only a pending bundle order item may be snapshotted.')
    components = BundleItem.objects.select_for_update().filter(bundle__product_id=item.product_id).select_related('product')
    for component in components:
        BundlePurchaseSnapshot.objects.get_or_create(order_item=item, product=component.product, defaults={
            'product_title': component.product.title, 'product_kind': component.product.kind, 'position': component.position,
        })


@transaction.atomic
def grant_purchase(item):
    order = Order.objects.select_for_update().get(pk=item.order_id)
    if order.status != 'paid':
        raise ValidationError('Purchase access requires a paid order.')
    products = list(item.bundlepurchasesnapshot_set.values_list('product_id', flat=True)) if item.product_kind == 'bundle' else [item.product_id]
    for product_id in products:
        entitlement, _ = Entitlement.objects.get_or_create(user_id=order.user_id, product_id=product_id)
        entitlement = Entitlement.objects.select_for_update().get(pk=entitlement.pk)
        grant, created = EntitlementGrant.objects.get_or_create(entitlement=entitlement, order_item=item, defaults={'grant_type': 'purchase'})
        if created:
            entitlement.status = 'active'
            entitlement.revoked_at = None
            entitlement.save(update_fields=['status', 'revoked_at', 'updated_at'])
            EntitlementEvent.objects.create(entitlement=entitlement, grant=grant, action='purchase_granted')


@transaction.atomic
def grant_manual(*, actor, user, product, reason):
    if not actor.is_active or not actor.has_perm('schema_v2.grant_manual_access') or not reason.strip():
        raise PermissionDenied('Manual access requires permission and an audit reason.')
    entitlement, _ = Entitlement.objects.get_or_create(user=user, product=product)
    entitlement = Entitlement.objects.select_for_update().get(pk=entitlement.pk)
    grant = EntitlementGrant.objects.create(entitlement=entitlement, grant_type='manual', granted_by=actor)
    entitlement.status = 'active'
    entitlement.revoked_at = None
    entitlement.save(update_fields=['status', 'revoked_at', 'updated_at'])
    EntitlementEvent.objects.create(entitlement=entitlement, grant=grant, actor=actor, action='manual_granted', reason=reason)
    AuditLog.objects.create(actor=actor, action='access.manual_granted', entity_type='entitlement_grants', entity_id=str(grant.pk), after_data={'reason': reason})
    return grant


@transaction.atomic
def complete_refund(*, refund_id, actor, provider_ref):
    if not actor.is_active or not actor.has_perm('schema_v2.change_refund'):
        raise PermissionDenied('Refund completion requires finance permission.')
    # Consistent order-first locking serializes refunds across attempts for the same purchase.
    initial = Refund.objects.select_related('payment').get(pk=refund_id)
    Order.objects.select_for_update().get(pk=initial.payment.order_id)
    refund = Refund.objects.select_for_update().get(pk=refund_id)
    if refund.status == 'completed':
        return refund
    if refund.status not in ['approved', 'processing']:
        raise ValidationError('Refund must be approved before completion.')
    refund.status = 'completed'
    refund.completed_at = timezone.now()
    refund.provider_ref = provider_ref
    refund.approved_by = actor
    refund.save()
    from django.db.models import Sum
    for allocation in RefundItem.objects.filter(refund=refund).select_related('order_item'):
        item = OrderItem.objects.select_for_update().get(pk=allocation.order_item_id)
        returned = RefundItem.objects.filter(order_item=item, refund__status='completed').aggregate(total=Sum('amount'))['total']
        if returned >= item.final_amount:
            for grant in EntitlementGrant.objects.select_for_update().filter(order_item=item, status='active'):
                entitlement = Entitlement.objects.select_for_update().get(pk=grant.entitlement_id)
                grant.status = 'revoked'
                grant.revoked_at = timezone.now()
                grant.save(update_fields=['status', 'revoked_at'])
                if not entitlement.entitlementgrant_set.filter(status='active').exists():
                    entitlement.status = 'revoked'
                    entitlement.revoked_at = timezone.now()
                    entitlement.save(update_fields=['status', 'revoked_at', 'updated_at'])
                EntitlementEvent.objects.create(entitlement=entitlement, grant=grant, actor=actor, action='refund_revoked', reason=refund.reason)
    AuditLog.objects.create(actor=actor, action='refund.completed', entity_type='refunds', entity_id=str(refund.pk), after_data={'provider_ref': provider_ref})
    return refund
