from django.db import migrations


SQL = r'''
CREATE FUNCTION v2_purchase_complete() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE oid bigint;
BEGIN
 IF TG_TABLE_NAME='orders' THEN oid:=NEW.id;
 ELSE SELECT order_id INTO oid FROM order_items WHERE id=COALESCE(NEW.order_item_id,OLD.order_item_id); END IF;
 IF NOT EXISTS(SELECT 1 FROM orders WHERE id=oid AND status='paid') THEN RETURN NULL; END IF;
 IF EXISTS(SELECT 1 FROM order_items oi JOIN orders o ON o.id=oi.order_id WHERE oi.order_id=oid AND oi.product_kind<>'bundle'
   AND NOT EXISTS(SELECT 1 FROM entitlement_grants g JOIN entitlements e ON e.id=g.entitlement_id WHERE g.order_item_id=oi.id AND e.product_id=oi.product_id AND e.user_id=o.user_id))
 THEN RAISE EXCEPTION 'Paid item requires purchase grant' USING ERRCODE='23514'; END IF;
 RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER purchase_complete AFTER INSERT OR UPDATE ON orders DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_purchase_complete();
CREATE CONSTRAINT TRIGGER purchase_complete AFTER INSERT OR UPDATE OR DELETE ON entitlement_grants DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_purchase_complete();

CREATE FUNCTION v2_bundle_composition_at_payment() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF NEW.status='paid' AND (TG_OP='INSERT' OR OLD.status<>'paid') AND EXISTS(
   SELECT 1 FROM order_items oi JOIN bundles b ON b.product_id=oi.product_id WHERE oi.order_id=NEW.id AND (
     EXISTS(SELECT product_id,position FROM bundle_items WHERE bundle_id=b.id EXCEPT SELECT product_id,position FROM bundle_purchase_snapshots WHERE order_item_id=oi.id)
     OR EXISTS(SELECT product_id,position FROM bundle_purchase_snapshots WHERE order_item_id=oi.id EXCEPT SELECT product_id,position FROM bundle_items WHERE bundle_id=b.id)
   )) THEN RAISE EXCEPTION 'Bundle snapshot must capture complete composition at payment' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER bundle_composition_at_payment BEFORE INSERT OR UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION v2_bundle_composition_at_payment();

CREATE FUNCTION v2_fixed_discount_check() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE pid bigint;
BEGIN
 IF TG_TABLE_NAME='promotions' THEN pid:=NEW.id;
 ELSIF TG_TABLE_NAME='promotion_products' THEN pid:=NEW.promotion_id;
 ELSE
   IF EXISTS(SELECT 1 FROM promotions p JOIN promotion_products pp ON pp.promotion_id=p.id WHERE pp.product_id=NEW.product_id AND p.discount_type='fixed' AND p.value>NEW.amount AND tstzrange(p.starts_at,p.ends_at,'[)') && tstzrange(NEW.valid_from,NEW.valid_until,'[)')) THEN RAISE EXCEPTION 'Price below applicable fixed discount' USING ERRCODE='23514'; END IF;
   RETURN NULL;
 END IF;
 PERFORM 1 FROM promotions WHERE id=pid FOR UPDATE;
 IF EXISTS(SELECT 1 FROM promotions p JOIN promotion_products pp ON pp.promotion_id=p.id JOIN product_prices pr ON pr.product_id=pp.product_id WHERE p.id=pid AND p.discount_type='fixed' AND p.value>pr.amount AND tstzrange(p.starts_at,p.ends_at,'[)') && tstzrange(pr.valid_from,pr.valid_until,'[)')) THEN RAISE EXCEPTION 'Fixed discount exceeds applicable price' USING ERRCODE='23514'; END IF;
 RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER fixed_discount_check AFTER INSERT OR UPDATE ON promotions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_fixed_discount_check();
CREATE CONSTRAINT TRIGGER fixed_discount_check AFTER INSERT OR UPDATE ON promotion_products DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_fixed_discount_check();
CREATE CONSTRAINT TRIGGER fixed_discount_check AFTER INSERT OR UPDATE ON product_prices DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_fixed_discount_check();
'''


class Migration(migrations.Migration):
    dependencies = [('schema_v2', '0003_hardening')]
    operations = [migrations.RunSQL(SQL)]
