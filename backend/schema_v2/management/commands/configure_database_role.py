"""Provision only the isolated local runtime role. Never echo credentials."""
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from psycopg2 import sql


class Command(BaseCommand):
    def handle(self, *args, **options):
        if connection.settings_dict['NAME'] != 'mezon_lms':
            raise CommandError('This command is restricted to mezon_lms.')
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname='mezon_app'")
            if not cursor.fetchone():
                cursor.execute(sql.SQL('CREATE ROLE mezon_app LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION').format(sql.Literal(os.environ['APP_DB_PASSWORD'])))
            cursor.execute('REVOKE ALL ON DATABASE mezon_lms FROM PUBLIC')
            cursor.execute('REVOKE CREATE ON SCHEMA public FROM PUBLIC')
            cursor.execute('GRANT CONNECT ON DATABASE mezon_lms TO mezon_app')
            cursor.execute('GRANT USAGE ON SCHEMA public TO mezon_app')
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename<>'django_migrations'")
            for (table,) in cursor.fetchall():
                privileges = 'SELECT, INSERT' if table in ['audit_logs', 'entitlement_events', 'review_moderations', 'bundle_purchase_snapshots'] else 'SELECT, INSERT, UPDATE, DELETE'
                cursor.execute(sql.SQL('GRANT {} ON TABLE {} TO mezon_app').format(sql.SQL(privileges), sql.Identifier(table)))
            cursor.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO mezon_app')
            cursor.execute('GRANT SELECT ON daily_sales, product_sales, payment_success_rate, refund_summary, course_completion, coupon_performance TO mezon_app')
            cursor.execute('REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM PUBLIC')
            cursor.execute("SELECT proname,pg_get_function_identity_arguments(p.oid) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND proname LIKE 'v2_%'")
            for name, arguments in cursor.fetchall():
                cursor.execute(sql.SQL('GRANT EXECUTE ON FUNCTION {}({}) TO mezon_app').format(sql.Identifier(name), sql.SQL(arguments)))
        self.stdout.write('Restricted mezon_app role configured; owner credentials remain separate.')
