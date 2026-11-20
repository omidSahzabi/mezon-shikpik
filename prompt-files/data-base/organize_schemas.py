"""One-time, database-only reorganization. No Django imports or data exports.

Run through the existing owner-credentialed Compose runner with Python stdin.
All moves and verification share one locked transaction; errors roll back DDL.
"""
import json
import os
import re

import psycopg2
from psycopg2 import sql


MAPPING = {
    'entity': 'users auth_group products categories courses lessons patterns bundles promotions coupons',
    'profiles': 'user_profiles staff_profiles instructor_profiles product_categories chapters lesson_assets pattern_variants pattern_releases pattern_files bundle_items promotion_products entitlements entitlement_grants lesson_progress reviews',
    'transactions': 'carts cart_items orders order_items order_discounts product_prices coupon_redemptions payment_attempts refunds refund_items',
    'events': 'audit_logs entitlement_events payment_events review_moderations bundle_purchase_snapshots django_migrations',
    'security': 'auth_permission auth_group_permissions users_groups users_user_permissions otp_challenges auth_sessions download_grants idempotency_keys django_content_type',
}
TABLES = {table: schema for schema, names in MAPPING.items() for table in names.split()}
VIEWS = set('daily_sales product_sales payment_success_rate refund_summary course_completion coupon_performance'.split())


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def qualify(body):
    # Preserve SQL string literals (including TG_TABLE_NAME comparisons), comments,
    # and quoted identifiers; qualify relation names and helper calls in code only.
    parts = re.split(r"('(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|--[^\n]*|/\*[\s\S]*?\*/)", body)
    for index in range(0, len(parts), 2):
        parts[index] = re.sub(r'(?<![\w.])(' + '|'.join(sorted(TABLES, key=len, reverse=True)) + r')\b', lambda m: TABLES[m[0]] + '.' + m[0], parts[index])
        parts[index] = re.sub(r'(?<![\w.])(v2_\w+)(?=\s*\()', r'public.\1', parts[index])
    return ''.join(parts)


def main():
    require(len(TABLES) == 50, 'Mapping must contain exactly 50 distinct tables.')
    conn = psycopg2.connect(dbname='mezon_lms', host=os.environ['POSTGRES_HOST'], port=os.environ['POSTGRES_PORT'], user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'])
    with conn:
        with conn.cursor() as cur:
            cur.execute("SET LOCAL lock_timeout='10s'; SET LOCAL statement_timeout='120s'")
            cur.execute('SELECT pg_advisory_xact_lock(6721152026)')
            cur.execute("SELECT c.oid,c.relname,n.nspname,c.relacl,c.relowner,c.relkind FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_toast%' AND c.relkind IN ('r','p','v','S','i','I') ORDER BY c.oid")
            objects = cur.fetchall()
            tables = [r for r in objects if r[5] in ('r','p')]
            require({r[1] for r in tables} == set(TABLES), 'Live tables differ from approved 50-table mapping.')
            require(all(r[2] == 'public' for r in tables), 'Expected pre-organization layout; refusing repeat execution.')
            cur.execute('LOCK TABLE ' + ','.join('public.' + name for name in sorted(TABLES)) + ' IN ACCESS EXCLUSIVE MODE')
            # Fingerprints remain in memory only; no row data or passwords leave PostgreSQL.
            fingerprints = {}
            for oid, name, *_ in tables:
                cur.execute(sql.SQL("SELECT count(*),md5(COALESCE(string_agg(md5(row_to_json(t)::text),'' ORDER BY md5(row_to_json(t)::text)),'')) FROM {} t").format(sql.Identifier('public', name)))
                fingerprints[oid] = cur.fetchone()
            cur.execute("SELECT oid,conrelid,confrelid,contype,convalidated,conkey,confkey,conbin::text,condeferrable,condeferred FROM pg_constraint WHERE connamespace='public'::regnamespace ORDER BY oid")
            constraints = cur.fetchall()
            require(all(r[4] for r in constraints), 'Preexisting unvalidated constraints.')
            cur.execute("SELECT t.oid,t.tgrelid,t.tgfoid,t.tgenabled,t.tgtype,t.tgdeferrable,t.tginitdeferred FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid WHERE c.relnamespace='public'::regnamespace ORDER BY t.oid")
            triggers = cur.fetchall()
            cur.execute("SELECT p.oid,pg_get_functiondef(p.oid),p.prosrc,p.proacl,p.proowner FROM pg_proc p WHERE p.pronamespace='public'::regnamespace AND p.proname LIKE 'v2_%' ORDER BY p.oid")
            functions = cur.fetchall()
            cur.execute("SELECT v.viewname FROM pg_views v WHERE v.schemaname='public'")
            require({r[0] for r in cur.fetchall()} == VIEWS, 'Unexpected reporting view inventory.')
            view_results = {}
            for name in sorted(VIEWS):
                cur.execute(sql.SQL('SELECT COALESCE(jsonb_agg(to_jsonb(v) ORDER BY to_jsonb(v)::text),\'[]\'::jsonb) FROM {} v').format(sql.Identifier('public', name)))
                view_results[name] = cur.fetchone()[0]
            cur.execute("SELECT c.oid,s.last_value FROM pg_class c JOIN pg_sequences s ON s.schemaname='public' AND s.sequencename=c.relname WHERE c.relkind='S' ORDER BY c.oid")
            sequence_values = cur.fetchall()
            # Inspect all dependency edges for the affected objects; moves retain OIDs.
            cur.execute("SELECT classid,objid,objsubid,refclassid,refobjid,refobjsubid,deptype FROM pg_depend WHERE objid=ANY(%s) OR refobjid=ANY(%s) ORDER BY 1,2,3,4,5,6,7", ([r[0] for r in objects], [r[0] for r in objects]))
            dependencies = cur.fetchall()
            for schema in [*MAPPING, 'analytics']:
                cur.execute(sql.SQL('CREATE SCHEMA {} AUTHORIZATION mezon_owner').format(sql.Identifier(schema)))
                cur.execute(sql.SQL('REVOKE ALL ON SCHEMA {} FROM PUBLIC').format(sql.Identifier(schema)))
                cur.execute(sql.SQL('GRANT USAGE ON SCHEMA {} TO mezon_app').format(sql.Identifier(schema)))
            for name, schema in sorted(TABLES.items()):
                cur.execute(sql.SQL('ALTER TABLE {} SET SCHEMA {}').format(sql.Identifier('public', name), sql.Identifier(schema)))
            for name in sorted(VIEWS):
                cur.execute(sql.SQL('ALTER VIEW {} SET SCHEMA analytics').format(sql.Identifier('public', name)))
            for oid, definition, body, acl, owner in functions:
                cur.execute(definition.replace(body, qualify(body), 1))
                cur.execute('SELECT %s::oid::regprocedure::text', [oid])
                identity = cur.fetchone()[0]
                cur.execute(sql.SQL('ALTER FUNCTION {} SET search_path TO pg_catalog, public, pg_temp').format(sql.SQL(identity)))
            cur.execute("SELECT c.oid,c.relname,n.nspname,c.relacl,c.relowner,c.relkind FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.oid=ANY(%s) ORDER BY c.oid", ([r[0] for r in objects],))
            after = cur.fetchall()
            require(len(after) == len(objects), 'Object lost during move.')
            for before, current in zip(objects, after):
                require(before[:2] == current[:2] and before[3:] == current[3:], 'OID, name, ACL, ownership or kind changed.')
            for oid, name, *_ in tables:
                cur.execute(sql.SQL("SELECT count(*),md5(COALESCE(string_agg(md5(row_to_json(t)::text),'' ORDER BY md5(row_to_json(t)::text)),'')) FROM {} t").format(sql.Identifier(TABLES[name], name)))
                require(cur.fetchone() == fingerprints[oid], 'Row fingerprint mismatch: ' + name)
            cur.execute('SELECT oid,conrelid,confrelid,contype,convalidated,conkey,confkey,conbin::text,condeferrable,condeferred FROM pg_constraint WHERE oid=ANY(%s) ORDER BY oid', ([r[0] for r in constraints],))
            require(cur.fetchall() == constraints, 'Constraint identity/definition changed.')
            cur.execute('SELECT oid,tgrelid,tgfoid,tgenabled,tgtype,tgdeferrable,tginitdeferred FROM pg_trigger WHERE oid=ANY(%s) ORDER BY oid', ([r[0] for r in triggers],))
            require(cur.fetchall() == triggers, 'Trigger identities or behavior flags changed.')
            for name in sorted(VIEWS):
                cur.execute(sql.SQL('SELECT COALESCE(jsonb_agg(to_jsonb(v) ORDER BY to_jsonb(v)::text),\'[]\'::jsonb) FROM {} v').format(sql.Identifier('analytics', name)))
                require(cur.fetchone()[0] == view_results[name], 'Reporting results changed: ' + name)
            cur.execute("SELECT c.oid,s.last_value FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_sequences s ON s.schemaname=n.nspname AND s.sequencename=c.relname WHERE c.oid=ANY(%s) ORDER BY c.oid", ([r[0] for r in sequence_values],))
            require(cur.fetchall() == sequence_values, 'Sequence state changed.')
            # Only namespace dependency edges are expected to change.
            cur.execute("SELECT 'pg_namespace'::regclass::oid")
            namespace_catalog = cur.fetchone()[0]
            cur.execute('SELECT classid,objid,objsubid,refclassid,refobjid,refobjsubid,deptype FROM pg_depend WHERE objid=ANY(%s) OR refobjid=ANY(%s) ORDER BY 1,2,3,4,5,6,7', ([r[0] for r in objects], [r[0] for r in objects]))
            require([r for r in dependencies if r[3] != namespace_catalog] == [r for r in cur.fetchall() if r[3] != namespace_catalog], 'Non-namespace dependency changed.')
            for oid, definition, body, acl, owner in functions:
                cur.execute('SELECT proacl,proowner FROM pg_proc WHERE oid=%s', [oid])
                require(cur.fetchone() == (acl, owner), 'Function ACL/owner changed.')
            cur.execute("SELECT count(*) FROM pg_tables WHERE schemaname='public'")
            require(cur.fetchone()[0] == 0, 'Tables remain in public.')
            cur.execute('SELECT public.v2_order_check(id) FROM transactions.orders')
            cur.execute('SELECT public.v2_access_check(id) FROM profiles.entitlements')
            cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
            # Recheck every physical FK against actual rows (including composite FKs).
            cur.execute("SELECT conrelid::regclass::text,confrelid::regclass::text,ARRAY(SELECT attname FROM unnest(conkey) WITH ORDINALITY k(num,pos) JOIN pg_attribute a ON a.attrelid=conrelid AND a.attnum=k.num ORDER BY k.pos),ARRAY(SELECT attname FROM unnest(confkey) WITH ORDINALITY k(num,pos) JOIN pg_attribute a ON a.attrelid=confrelid AND a.attnum=k.num ORDER BY k.pos) FROM pg_constraint WHERE oid=ANY(%s) AND contype='f'", ([r[0] for r in constraints],))
            for child, parent, child_columns, parent_columns in cur.fetchall():
                joins = ' AND '.join('c.' + a + '=p.' + b for a,b in zip(child_columns,parent_columns))
                nonnull = ' AND '.join('c.' + a + ' IS NOT NULL' for a in child_columns)
                cur.execute('SELECT NOT EXISTS(SELECT 1 FROM '+child+' c WHERE '+nonnull+' AND NOT EXISTS(SELECT 1 FROM '+parent+' p WHERE '+joins+'))')
                require(cur.fetchone()[0], 'Orphan foreign key: '+child)
            # Positive deferred trigger exercises, discarded so all demo rows stay unchanged.
            cur.execute('SAVEPOINT trigger_probe')
            cur.execute('UPDATE entity.courses SET summary=summary; UPDATE profiles.entitlements SET status=status; UPDATE profiles.reviews SET body=body; UPDATE transactions.product_prices SET amount=amount; SET CONSTRAINTS ALL IMMEDIATE')
            cur.execute('ROLLBACK TO SAVEPOINT trigger_probe')
            for statement in [
                "UPDATE transactions.orders SET order_number=order_number||'-probe'",
                'UPDATE transactions.payment_attempts SET amount=amount',
                'UPDATE events.audit_logs SET action=action',
                'UPDATE events.entitlement_events SET action=action',
                "UPDATE entity.products SET status='draft' WHERE status='published'",
                "INSERT INTO transactions.orders(id,order_number,user_id,subtotal,payable_total) SELECT -672115,'SCHEMA-VERIFY-ROLLBACK',id,100,100 FROM entity.users ORDER BY id LIMIT 1",
            ]:
                cur.execute('SAVEPOINT invalid_probe')
                try:
                    cur.execute(statement)
                    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
                except psycopg2.Error as error:
                    require(error.pgcode == '23514', 'Unexpected probe failure: '+error.pgcode)
                    cur.execute('ROLLBACK TO SAVEPOINT invalid_probe')
                else:
                    raise RuntimeError('Invalid mutation was accepted: '+statement)
            cur.execute('SET LOCAL ROLE mezon_app')
            for name in VIEWS:
                cur.execute(sql.SQL('SELECT count(*) FROM {}').format(sql.Identifier('analytics',name)))
            cur.execute('SELECT public.v2_order_check(id) FROM transactions.orders')
            cur.execute('SELECT public.v2_access_check(id) FROM profiles.entitlements')
            cur.execute('RESET ROLE')
            cur.execute('SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal AND oid=ANY(%s)', ([r[0] for r in triggers],))
            custom_triggers = cur.fetchone()[0]
            print(json.dumps({'tables': len(tables), 'rows_unchanged': sum(r[0] for r in fingerprints.values()), 'constraints': len(constraints), 'foreign_keys': sum(r[3]=='f' for r in constraints), 'custom_triggers': custom_triggers, 'functions':len(functions), 'views':len(VIEWS), 'sequences':len(sequence_values), 'dependency_edges':len(dependencies), 'mapping':{k:len(v.split()) for k,v in MAPPING.items()}}, sort_keys=True))
    print('COMMITTED: all 50 table fingerprints, object identities, ACLs, sequence values, dependencies and reporting results preserved.')


if __name__ == '__main__':
    main()
