import os
from pathlib import Path

import psycopg2
from django.apps import apps
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from schema_v2.models import (
    Course, Entitlement, EntitlementGrant, InstructorProfile, Lesson, Order,
    OrderItem, Pattern, PatternFile, PatternRelease, PatternVariant,
    PaymentAttempt, Review, User,
)


class Command(BaseCommand):
    help = 'Verify demo data, tables, constraints, auth and runtime RBAC; runtime write probe is rolled back.'

    def handle(self, *args, **options):
        def require(condition, message):
            if not condition:
                raise CommandError(message)

        require(connection.settings_dict['NAME'] == 'mezon_lms', 'Wrong database.')
        with connection.cursor() as cursor:
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
            tables = {row[0] for row in cursor.fetchall()}
            expected = {m._meta.db_table for m in apps.get_models(include_auto_created=True)}
            require(expected <= tables, f'Missing model tables: {expected-tables}')
            cursor.execute("SELECT viewname FROM pg_views WHERE schemaname='public'")
            views = {row[0] for row in cursor.fetchall()}
            require(views == {'daily_sales','product_sales','payment_success_rate','refund_summary','course_completion','coupon_performance'}, 'Reporting views mismatch.')
            cursor.execute("SELECT count(*) FROM pg_constraint WHERE connamespace='public'::regnamespace AND NOT convalidated")
            require(cursor.fetchone()[0] == 0, 'Unvalidated constraints exist.')
            cursor.execute("SELECT count(*) FROM pg_constraint WHERE connamespace='public'::regnamespace AND contype='f'")
            fks = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM pg_constraint WHERE connamespace='public'::regnamespace AND contype='c'")
            checks = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal AND tgrelid IN (SELECT oid FROM pg_class WHERE relnamespace='public'::regnamespace)")
            triggers = cursor.fetchone()[0]
            cursor.execute('SELECT sum(order_count),sum(sales_amount),sum(captured_amount),sum(refunded_amount) FROM daily_sales')
            require(tuple(cursor.fetchone()) == (3,13500000,13500000,0), 'Sales figures mismatch.')
            for name in views:
                cursor.execute(f'SELECT * FROM {name} LIMIT 1')
            cursor.execute('SELECT id FROM orders')
            for (oid,) in cursor.fetchall():
                cursor.execute('SELECT v2_order_check(%s)', [oid])
            cursor.execute('SELECT id FROM entitlements')
            for (eid,) in cursor.fetchall():
                cursor.execute('SELECT v2_access_check(%s)', [eid])
        require(User.objects.count() == 7, 'Expected 7 users.')
        require(InstructorProfile.objects.count() == 2, 'Expected 2 instructor profiles.')
        require(Course.objects.count() == 2 and Lesson.objects.filter(is_published=True).count() == 6, 'Course fixture mismatch.')
        require(Pattern.objects.count() == 3 and PatternVariant.objects.count() == 9 and PatternRelease.objects.filter(status='published').count() == 3 and PatternFile.objects.count() == 9, 'Pattern fixture mismatch.')
        require(Entitlement.objects.filter(status='active', product__kind='course').count() == 6, 'Expected six active course entitlements.')
        require(EntitlementGrant.objects.filter(grant_type='purchase',status='active').count() == 6, 'Expected six purchase grants.')
        require(Order.objects.filter(status='paid').count() == 3 and OrderItem.objects.count() == 6 and PaymentAttempt.objects.filter(status='succeeded',provider='mock').count() == 3, 'Purchase fixture mismatch.')
        require(Review.objects.filter(status='approved').count() == 2, 'Expected two approved reviews.')
        for review in Review.objects.all():
            require(EntitlementGrant.objects.filter(entitlement__user=review.user,entitlement__product=review.product,grant_type='purchase').exists(), 'Review lacks purchaser.')
        require(Group.objects.get(name='Student').permissions.count() == 0, 'Student must not have global model permissions.')
        require(not Group.objects.get(name='Support').permissions.filter(codename='change_refund').exists(), 'Support may not approve refunds.')
        require(Group.objects.get(name='Instructor').permissions.filter(codename='change_course').exists(), 'Instructor content permissions missing.')
        for user in User.objects.all():
            require(user.groups.count() == 1, 'Missing or duplicate demo role.')
            require(user.password.startswith('argon2$argon2id$'), 'Password is not Argon2id.')
        # Parse only in-process for authentication; never print credential contents.
        verified = set()
        for line in Path(os.environ.get('LOCAL_CREDENTIALS_PATH','/local-credentials.md')).read_text(encoding='utf-8').splitlines():
            cells = [cell.strip() for cell in line.split('|')]
            if len(cells) == 5 and cells[1].startswith('+989'):
                require(authenticate(phone=cells[1],password=cells[3]) is not None, 'Test authentication failed.')
                verified.add(cells[1])
        require(len(verified)==7, 'Expected credentials for all seven users.')
        runtime = dict(connection.settings_dict)
        with psycopg2.connect(dbname='mezon_lms',host=runtime['HOST'],port=runtime['PORT'],user='mezon_app',password=os.environ['APP_DB_PASSWORD']) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT rolsuper,rolcreatedb,rolcreaterole FROM pg_roles WHERE rolname=current_user")
                require(cursor.fetchone() == (False,False,False), 'Runtime role is privileged.')
                cursor.execute("SELECT has_schema_privilege(current_user,'public','CREATE'),has_table_privilege(current_user,'audit_logs','UPDATE'),has_table_privilege(current_user,'django_migrations','SELECT')")
                require(cursor.fetchone()==(False,False,False), 'Runtime DDL/history/migration privilege leak.')
                cursor.execute('SELECT count(*) FROM daily_sales')
                require(cursor.fetchone()[0] > 0, 'Runtime cannot read reports.')
                cursor.execute('SAVEPOINT runtime_probe')
                cursor.execute("INSERT INTO orders (public_id,order_number,user_id,status,subtotal,discount_total,payable_total,currency) SELECT gen_random_uuid(),'VALIDATION-RUNTIME',id,'pending',0,0,0,'IRR' FROM users ORDER BY id LIMIT 1")
                cursor.execute('SET CONSTRAINTS ALL IMMEDIATE')
                cursor.execute('ROLLBACK TO SAVEPOINT runtime_probe')
        self.stdout.write(f'PASS: {len(tables)} tables, {len(views)} views, {fks} FKs, {checks} CHECKs, {triggers} triggers; 7 authenticated users; RBAC; 6 course entitlements; 2 purchaser reviews; finance and runtime permissions.')
