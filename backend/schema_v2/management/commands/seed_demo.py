"""Small deterministic fixture; passwords generated only for newly created users."""
import os
import secrets
from pathlib import Path

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from schema_v2.models import (
    AuditLog, Category, Chapter, Course, Entitlement, EntitlementEvent,
    EntitlementGrant, InstructorProfile, Lesson, Order, OrderItem, Pattern,
    PatternFile, PatternRelease, PatternVariant, PaymentAttempt, Product,
    ProductCategory, ProductPrice, Review, ReviewModeration, StaffProfile,
    User, UserProfile,
)


class Command(BaseCommand):
    help = 'Seed fictional Persian demo data into the isolated mezon_lms database.'

    def handle(self, *args, **options):
        from django.db import connection
        if connection.settings_dict['NAME'] != 'mezon_lms':
            raise CommandError('Refusing to seed any database other than mezon_lms.')
        credentials = Path(os.environ.get('LOCAL_CREDENTIALS_PATH', '/local-credentials.md'))
        if not credentials.is_file():
            raise CommandError('Create the ignored local credentials file first.')
        # Serialize seed runs. Write credentials before commit so a write failure rolls back users.
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute('SELECT pg_advisory_xact_lock(6721142026)')
            self.seed(credentials)
        self.stdout.write(self.style.SUCCESS('Demo seed complete (idempotent). No passwords logged.'))

    def seed(self, credentials):
        now = timezone.now()
        groups = {name: Group.objects.get_or_create(name=name)[0] for name in ['Admin', 'Instructor', 'Support', 'Student']}
        permissions = Permission.objects.filter(content_type__app_label='schema_v2')
        groups['Admin'].permissions.set(Permission.objects.all())
        content = ['course', 'chapter', 'lesson', 'lessonasset', 'pattern', 'patternvariant', 'patternrelease', 'patternfile']
        groups['Instructor'].permissions.set(permissions.filter(content_type__model__in=content, codename__regex=r'^(view|add|change)_'))
        groups['Support'].permissions.set(permissions.filter(codename__in=['view_user', 'view_userprofile', 'view_order', 'view_orderitem', 'view_paymentattempt', 'view_entitlement', 'view_review', 'change_review', 'add_reviewmoderation', 'view_refund', 'add_refund']))
        groups['Student'].permissions.clear()  # Personal data requires ownership, not global model permissions.
        people = [
            ('Admin', 'آرمان', 'نیک‌روش'), ('Support', 'نرگس', 'مهربان'),
            ('Instructor', 'سارا', 'پارسا'), ('Instructor', 'مریم', 'راد'),
            ('Student', 'لیلا', 'بهمنی'), ('Student', 'بهار', 'فرهمند'), ('Student', 'پریسا', 'آزاد'),
        ]
        users = []
        credential_lines = []
        for i, (role, first, last) in enumerate(people):
            phone = f'+98900000010{i}'
            user, created = User.objects.get_or_create(phone=phone, defaults={'is_staff': role in ['Admin', 'Support'], 'is_superuser': role == 'Admin'})
            if created:
                password = secrets.token_urlsafe(24)
                user.set_password(password)
                user.save(update_fields=['password'])
                credential_lines.append(f'| {phone} | {role} | {password} |')
            user.groups.add(groups[role])
            UserProfile.objects.get_or_create(user=user, defaults={'first_name': first, 'last_name': last})
            if role == 'Instructor':
                InstructorProfile.objects.get_or_create(user=user, defaults={'display_name': f'{first} {last}', 'bio': 'مدرس داستانی آموزش دوخت و الگوسازی', 'is_public': True})
            if role in ['Admin', 'Support']:
                StaffProfile.objects.get_or_create(user=user, defaults={'display_name': f'{first} {last}'})
            if created:
                AuditLog.objects.create(actor=user, action='demo.user_created', entity_type='users', entity_id=str(user.pk), after_data={'role': role})
            users.append(user)
        category, _ = Category.objects.get_or_create(slug='sewing', defaults={'name': 'آموزش خیاطی'})
        courses = []
        for i, title in enumerate(['آموزش دوخت دامن پایه', 'آموزش دوخت مانتوی روزمره']):
            product, _ = Product.objects.get_or_create(slug=f'demo-course-{i+1}', defaults={'title': title, 'kind': 'course', 'status': 'published', 'description': 'آموزش مرحله به مرحله از اندازه‌گیری تا دوخت نهایی', 'published_at': now})
            course, _ = Course.objects.get_or_create(product=product, defaults={'instructor_id': users[i+2].pk, 'summary': 'تمرین عملی برای هنرجویان مبتدی', 'estimated_minutes': 90})
            chapter, _ = Chapter.objects.get_or_create(course=course, position=0, defaults={'title': 'آماده‌سازی و دوخت', 'is_published': True})
            for j, lesson in enumerate(['اندازه‌گیری و شناخت ابزار', 'رسم الگو و برش پارچه', 'دوخت و پرداخت نهایی']):
                Lesson.objects.get_or_create(chapter=chapter, position=j, defaults={'title': lesson, 'duration_seconds': 1800, 'is_published': True})
            ProductCategory.objects.get_or_create(product=product, category=category)
            ProductPrice.objects.get_or_create(product=product, defaults={'amount': (i+1)*1500000, 'valid_from': now})
            courses.append(product)
        for i, title in enumerate(['الگوی دامن راسته', 'الگوی شومیز ساده', 'الگوی مانتو آزاد']):
            product, _ = Product.objects.get_or_create(slug=f'demo-pattern-{i+1}', defaults={'title': title, 'kind': 'pattern', 'status': 'published', 'published_at': now})
            pattern, _ = Pattern.objects.get_or_create(product=product, defaults={'description': 'الگوی آزمایشی مناسب چاپ خانگی، بدون فایل واقعی'})
            release, _ = PatternRelease.objects.get_or_create(pattern=pattern, version='1.0', defaults={'status': 'published', 'released_at': now})
            for j, size in enumerate(['۳۶', '۳۸', '۴۰']):
                variant, _ = PatternVariant.objects.get_or_create(pattern=pattern, size_label=size, defaults={'sort_order': j})
                PatternFile.objects.get_or_create(release=release, variant=variant, file_kind='a4_pdf', defaults={'pattern': pattern, 'storage_key': f'demo/placeholders/pattern-{i+1}/size-{j}.pdf', 'checksum_sha256': '0'*64, 'size_bytes': 1024, 'display_name': f'{title} سایز {size}'})
            ProductCategory.objects.get_or_create(product=product, category=category)
            ProductPrice.objects.get_or_create(product=product, defaults={'amount': 350000, 'valid_from': now})
        for student in users[4:]:
            prices = [p.productprice_set.get().amount for p in courses]
            order, _ = Order.objects.get_or_create(order_number=f'DEMO-{student.pk}', defaults={'user': student, 'subtotal': sum(prices), 'payable_total': sum(prices)})
            items = []
            for product, price in zip(courses, prices):
                item, _ = OrderItem.objects.get_or_create(order=order, product=product, defaults={'product_title': product.title, 'product_kind': product.kind, 'unit_price': price, 'final_amount': price})
                items.append(item)
            PaymentAttempt.objects.get_or_create(idempotency_key=f'demo-payment-{student.pk}', defaults={'order': order, 'provider': 'mock', 'authority': f'demo-authority-{student.pk}', 'reference': f'demo-reference-{student.pk}', 'amount': order.payable_total, 'status': 'succeeded', 'verified_at': now})
            if order.status != 'paid':
                order.status = 'paid'
                order.paid_at = now
                order.save(update_fields=['status', 'paid_at', 'updated_at'])
            for item in items:
                entitlement, _ = Entitlement.objects.get_or_create(user=student, product=item.product)
                grant, created = EntitlementGrant.objects.get_or_create(entitlement=entitlement, order_item=item, defaults={'grant_type': 'purchase'})
                if created:
                    EntitlementEvent.objects.create(entitlement=entitlement, grant=grant, action='purchase_granted', reason='خرید آزمایشی با پرداخت ساختگی')
        for student, rating in zip(users[4:6], [5, 4]):
            review, created = Review.objects.get_or_create(user=student, product=courses[0], defaults={'rating': rating, 'title': 'آموزش کاربردی و روشن', 'body': 'مراحل برش و دوخت به خوبی توضیح داده شده است.', 'status': 'approved', 'moderated_by': users[1], 'moderated_at': now})
            if created:
                ReviewModeration.objects.create(review=review, moderator=users[1], action='approved', reason='بررسی نظر خریدار آزمایشی')
        if credential_lines:
            with credentials.open('a', encoding='utf-8') as output:
                output.write('\n| Phone | Application role | Test password |\n|---|---|---|\n' + '\n'.join(credential_lines) + '\n')
