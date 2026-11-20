from django.db import migrations

# Frozen PostgreSQL schema SQL; append migrations for future changes.
SQL = r'''

ALTER TABLE users ALTER COLUMN public_id SET DEFAULT gen_random_uuid();
ALTER TABLE orders ALTER COLUMN public_id SET DEFAULT gen_random_uuid();
ALTER TABLE payment_attempts ALTER COLUMN public_id SET DEFAULT gen_random_uuid();
ALTER TABLE users ALTER COLUMN is_superuser SET DEFAULT false;
ALTER TABLE auth_sessions ADD CONSTRAINT auth_session_hash_format CHECK(token_hash ~ '^[a-f0-9]{64}$');
ALTER TABLE download_grants ADD CONSTRAINT download_hash_format CHECK(token_hash ~ '^[a-f0-9]{64}$');
ALTER TABLE idempotency_keys ADD CONSTRAINT request_hash_format CHECK(request_hash ~ '^[a-f0-9]{64}$');
ALTER TABLE pattern_files ADD CONSTRAINT file_hash_format CHECK(checksum_sha256 ~ '^[a-f0-9]{64}$');
ALTER TABLE otp_challenges ADD CONSTRAINT otp_phone_format CHECK(phone ~ '^\+[1-9][0-9]{7,14}$');
ALTER TABLE entitlement_grants ADD CONSTRAINT grant_revocation_time CHECK ((status='revoked')=(revoked_at IS NOT NULL));
ALTER TABLE entitlements ADD CONSTRAINT access_revocation_time CHECK ((status='revoked')=(revoked_at IS NOT NULL));

CREATE FUNCTION v2_refund_allocation_guard() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE rid bigint;
BEGIN
 rid:=CASE WHEN TG_OP='INSERT' THEN NEW.refund_id ELSE OLD.refund_id END;
 PERFORM 1 FROM refunds WHERE id=rid AND status='completed' FOR UPDATE;
 IF FOUND THEN RAISE EXCEPTION 'Completed refund allocation is immutable' USING ERRCODE='23514'; END IF;
 IF TG_OP='DELETE' THEN RETURN OLD; END IF; RETURN NEW;
END $$;
CREATE TRIGGER refund_allocation_guard BEFORE INSERT OR UPDATE OR DELETE ON refund_items FOR EACH ROW EXECUTE FUNCTION v2_refund_allocation_guard();

CREATE FUNCTION v2_identity_guard() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE k text; oldrow jsonb:=to_jsonb(OLD); newrow jsonb:=to_jsonb(NEW);
BEGIN
 FOR k IN SELECT jsonb_object_keys(oldrow) LOOP
   IF (k='id' OR k LIKE '%\_id' ESCAPE '\') AND oldrow->k IS DISTINCT FROM newrow->k THEN
     RAISE EXCEPTION 'Identity and relationship reassignment forbidden: %.%',TG_TABLE_NAME,k USING ERRCODE='23514';
   END IF;
 END LOOP;
 RETURN NEW;
END $$;

CREATE FUNCTION v2_purchase_coverage() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE oid bigint; eid bigint; rowdata jsonb;
BEGIN
 rowdata:=CASE WHEN TG_OP='DELETE' THEN to_jsonb(OLD) ELSE to_jsonb(NEW) END;
 IF TG_TABLE_NAME='orders' THEN oid:=(rowdata->>'id')::bigint;
 ELSIF TG_TABLE_NAME='entitlement_grants' OR TG_TABLE_NAME='bundle_purchase_snapshots' THEN
   SELECT order_id INTO oid FROM order_items WHERE id=(rowdata->>'order_item_id')::bigint;
 ELSE SELECT p.order_id INTO oid FROM payment_attempts p WHERE p.id=(rowdata->>'payment_id')::bigint;
 END IF;
 FOR eid IN SELECT DISTINCT g.entitlement_id FROM entitlement_grants g JOIN order_items oi ON oi.id=g.order_item_id WHERE oi.order_id=oid LOOP
   PERFORM v2_access_check(eid);
 END LOOP;
 IF EXISTS(SELECT 1 FROM orders WHERE id=oid AND status='paid') THEN
   IF EXISTS(SELECT 1 FROM bundle_purchase_snapshots s JOIN order_items oi ON oi.id=s.order_item_id JOIN orders o ON o.id=oi.order_id
      WHERE oi.order_id=oid AND NOT EXISTS(SELECT 1 FROM entitlement_grants g JOIN entitlements e ON e.id=g.entitlement_id WHERE g.order_item_id=oi.id AND e.product_id=s.product_id AND e.user_id=o.user_id))
   THEN RAISE EXCEPTION 'Bundle snapshot missing purchase grants' USING ERRCODE='23514'; END IF;
 END IF;
 RETURN NULL;
END $$;

CREATE FUNCTION v2_catalog_guard() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF TG_TABLE_NAME='products' THEN
   IF NEW.kind<>OLD.kind THEN RAISE EXCEPTION 'Product kind is immutable' USING ERRCODE='23514'; END IF;
 ELSIF TG_TABLE_NAME='order_items' THEN
   IF NOT EXISTS(SELECT 1 FROM products WHERE id=NEW.product_id AND kind=NEW.product_kind AND title=NEW.product_title) THEN RAISE EXCEPTION 'Order item snapshot mismatch' USING ERRCODE='23514'; END IF;
 ELSIF TG_TABLE_NAME='promotions' THEN
   IF NEW.discount_type='fixed' AND EXISTS(SELECT 1 FROM promotion_products pp JOIN product_prices pr ON pr.product_id=pp.product_id WHERE pp.promotion_id=NEW.id AND tstzrange(pr.valid_from,pr.valid_until,'[)') && tstzrange(NEW.starts_at,NEW.ends_at,'[)') AND pr.amount<NEW.value) THEN RAISE EXCEPTION 'Fixed promotion exceeds price' USING ERRCODE='23514'; END IF;
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER product_kind_guard BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION v2_catalog_guard();
CREATE TRIGGER item_snapshot_guard BEFORE INSERT ON order_items FOR EACH ROW EXECUTE FUNCTION v2_catalog_guard();
CREATE TRIGGER fixed_promotion_guard BEFORE INSERT OR UPDATE ON promotions FOR EACH ROW EXECUTE FUNCTION v2_catalog_guard();
CREATE TRIGGER identity_guard BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION v2_identity_guard();
CREATE TRIGGER identity_guard BEFORE UPDATE ON order_items FOR EACH ROW EXECUTE FUNCTION v2_identity_guard();
CREATE TRIGGER identity_guard BEFORE UPDATE ON order_discounts FOR EACH ROW EXECUTE FUNCTION v2_identity_guard();
CREATE TRIGGER identity_guard BEFORE UPDATE ON payment_attempts FOR EACH ROW EXECUTE FUNCTION v2_identity_guard();
CREATE TRIGGER identity_guard BEFORE UPDATE ON refunds FOR EACH ROW EXECUTE FUNCTION v2_identity_guard();
CREATE TRIGGER identity_guard BEFORE UPDATE ON refund_items FOR EACH ROW EXECUTE FUNCTION v2_identity_guard();
CREATE TRIGGER identity_guard BEFORE UPDATE ON entitlements FOR EACH ROW EXECUTE FUNCTION v2_identity_guard();
CREATE TRIGGER identity_guard BEFORE UPDATE ON entitlement_grants FOR EACH ROW EXECUTE FUNCTION v2_identity_guard();
CREATE TRIGGER identity_guard BEFORE UPDATE ON courses FOR EACH ROW EXECUTE FUNCTION v2_identity_guard();
CREATE TRIGGER identity_guard BEFORE UPDATE ON patterns FOR EACH ROW EXECUTE FUNCTION v2_identity_guard();
CREATE TRIGGER identity_guard BEFORE UPDATE ON bundles FOR EACH ROW EXECUTE FUNCTION v2_identity_guard();
CREATE TRIGGER identity_guard BEFORE UPDATE ON pattern_files FOR EACH ROW EXECUTE FUNCTION v2_identity_guard();
CREATE TRIGGER identity_guard BEFORE UPDATE ON pattern_releases FOR EACH ROW EXECUTE FUNCTION v2_identity_guard();
CREATE TRIGGER identity_guard BEFORE UPDATE ON pattern_variants FOR EACH ROW EXECUTE FUNCTION v2_identity_guard();
CREATE CONSTRAINT TRIGGER purchase_coverage AFTER INSERT OR UPDATE OR DELETE ON orders DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_purchase_coverage();
CREATE CONSTRAINT TRIGGER purchase_coverage AFTER INSERT OR UPDATE OR DELETE ON refunds DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_purchase_coverage();
CREATE CONSTRAINT TRIGGER purchase_coverage AFTER INSERT OR UPDATE OR DELETE ON entitlement_grants DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_purchase_coverage();
CREATE CONSTRAINT TRIGGER purchase_coverage AFTER INSERT OR UPDATE OR DELETE ON bundle_purchase_snapshots DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_purchase_coverage();
'''

class Migration(migrations.Migration):
    dependencies = [('schema_v2', '0002_integrity_and_reports')]
    operations = [migrations.RunSQL(SQL)]
