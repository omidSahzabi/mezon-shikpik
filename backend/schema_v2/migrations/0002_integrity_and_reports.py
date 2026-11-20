from django.db import migrations

# Frozen PostgreSQL schema SQL; append migrations for future changes.
SQL = r'''

ALTER TABLE pattern_files ADD CONSTRAINT file_release_pattern_fk
 FOREIGN KEY (release_id,pattern_id) REFERENCES pattern_releases(id,pattern_id) ON DELETE RESTRICT;
ALTER TABLE pattern_files ADD CONSTRAINT file_variant_pattern_fk
 FOREIGN KEY (variant_id,pattern_id) REFERENCES pattern_variants(id,pattern_id) ON DELETE RESTRICT;
ALTER TABLE order_discounts ADD CONSTRAINT discount_same_order_fk
 FOREIGN KEY (order_item_id,order_id) REFERENCES order_items(id,order_id) ON DELETE RESTRICT;

CREATE FUNCTION v2_immutable() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'Immutable history: %', TG_TABLE_NAME USING ERRCODE='23514'; END $$;

CREATE FUNCTION v2_order_check(oid bigint) RETURNS void LANGUAGE plpgsql AS $$
DECLARE o orders; r refunds; p payment_attempts;
BEGIN
 SELECT * INTO o FROM orders WHERE id=oid FOR UPDATE;
 IF NOT FOUND THEN RETURN; END IF;
 IF o.subtotal <> (SELECT COALESCE(sum(unit_price),0) FROM order_items WHERE order_id=oid)
 OR o.discount_total <> (SELECT COALESCE(sum(discount_amount),0) FROM order_items WHERE order_id=oid)
 OR o.payable_total <> (SELECT COALESCE(sum(final_amount),0) FROM order_items WHERE order_id=oid)
 OR o.discount_total <> (SELECT COALESCE(sum(amount),0) FROM order_discounts WHERE order_id=oid)
 THEN RAISE EXCEPTION 'Order snapshot totals mismatch: %',oid USING ERRCODE='23514'; END IF;
 IF o.status='paid' AND NOT EXISTS (SELECT 1 FROM payment_attempts WHERE order_id=oid AND status='succeeded' AND amount=o.payable_total)
 THEN RAISE EXCEPTION 'Paid order requires captured payment' USING ERRCODE='23514'; END IF;
 IF EXISTS(SELECT 1 FROM payment_attempts WHERE order_id=oid AND status='succeeded' AND amount<>o.payable_total)
 THEN RAISE EXCEPTION 'Captured amount differs from order' USING ERRCODE='23514'; END IF;
 FOR r IN SELECT rf.* FROM refunds rf JOIN payment_attempts pa ON pa.id=rf.payment_id WHERE pa.order_id=oid LOOP
   SELECT * INTO p FROM payment_attempts WHERE id=r.payment_id;
   IF r.amount<>(SELECT COALESCE(sum(amount),0) FROM refund_items WHERE refund_id=r.id)
   OR EXISTS(SELECT 1 FROM refund_items ri JOIN order_items oi ON oi.id=ri.order_item_id WHERE ri.refund_id=r.id AND oi.order_id<>oid)
   OR p.status<>'succeeded'
   THEN RAISE EXCEPTION 'Invalid refund allocation' USING ERRCODE='23514'; END IF;
 END LOOP;
 IF EXISTS(SELECT 1 FROM payment_attempts pa WHERE pa.order_id=oid AND
   (SELECT COALESCE(sum(amount),0) FROM refunds WHERE payment_id=pa.id AND status NOT IN ('failed','rejected'))>pa.amount)
 OR EXISTS(SELECT 1 FROM order_items oi WHERE oi.order_id=oid AND
   (SELECT COALESCE(sum(ri.amount),0) FROM refund_items ri JOIN refunds rf ON rf.id=ri.refund_id WHERE ri.order_item_id=oi.id AND rf.status NOT IN ('failed','rejected'))>oi.final_amount)
 THEN RAISE EXCEPTION 'Refund exceeds available balance' USING ERRCODE='23514'; END IF;
 IF EXISTS(SELECT 1 FROM order_items oi WHERE oi.order_id=oid AND oi.product_kind='bundle'
   AND NOT EXISTS(SELECT 1 FROM bundle_purchase_snapshots WHERE order_item_id=oi.id))
 THEN RAISE EXCEPTION 'Bundle purchase requires immutable composition snapshot' USING ERRCODE='23514'; END IF;
END $$;

CREATE FUNCTION v2_finance_deferred() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE rowdata jsonb; oid bigint;
BEGIN
 rowdata := CASE WHEN TG_OP='DELETE' THEN to_jsonb(OLD) ELSE to_jsonb(NEW) END;
 IF TG_TABLE_NAME='orders' THEN oid:=(rowdata->>'id')::bigint;
 ELSIF TG_TABLE_NAME IN ('order_items','order_discounts','payment_attempts') THEN oid:=(rowdata->>'order_id')::bigint;
 ELSIF TG_TABLE_NAME='refunds' THEN SELECT order_id INTO oid FROM payment_attempts WHERE id=(rowdata->>'payment_id')::bigint;
 ELSIF TG_TABLE_NAME='refund_items' THEN SELECT pa.order_id INTO oid FROM refunds r JOIN payment_attempts pa ON pa.id=r.payment_id WHERE r.id=(rowdata->>'refund_id')::bigint;
 ELSE SELECT order_id INTO oid FROM order_items WHERE id=(rowdata->>'order_item_id')::bigint;
 END IF;
 PERFORM v2_order_check(oid);
 RETURN NULL;
END $$;

CREATE FUNCTION v2_settled_guard() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE oid bigint; settled boolean;
BEGIN
 IF TG_TABLE_NAME='orders' THEN
   IF OLD.status='paid' AND (TG_OP='DELETE' OR NEW IS DISTINCT FROM OLD) THEN
     RAISE EXCEPTION 'Paid order is immutable' USING ERRCODE='23514';
   END IF;
 ELSIF TG_TABLE_NAME='payment_attempts' THEN
   IF OLD.status='succeeded' THEN RAISE EXCEPTION 'Captured payment is immutable' USING ERRCODE='23514'; END IF;
 ELSIF TG_TABLE_NAME='refunds' THEN
   IF OLD.status='completed' THEN RAISE EXCEPTION 'Completed refund is immutable' USING ERRCODE='23514'; END IF;
 ELSE
   IF TG_OP='INSERT' THEN oid:=NEW.order_id; ELSE oid:=OLD.order_id; END IF;
   SELECT status='paid' INTO settled FROM orders WHERE id=oid FOR UPDATE;
   IF settled THEN RAISE EXCEPTION 'Settled order snapshots are immutable' USING ERRCODE='23514'; END IF;
 END IF;
 IF TG_OP='DELETE' THEN RETURN OLD; END IF; RETURN NEW;
END $$;

CREATE FUNCTION v2_transition() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE allowed text[];
BEGIN
 IF NEW.status=OLD.status THEN RETURN NEW; END IF;
 IF TG_TABLE_NAME='orders' THEN
   IF OLD.status='pending' THEN allowed:=ARRAY['paid','cancelled','expired']; END IF;
 ELSIF TG_TABLE_NAME='payment_attempts' THEN
   IF OLD.status IN ('initiated','pending') THEN allowed:=ARRAY['pending','succeeded','failed','cancelled']; END IF;
 ELSIF TG_TABLE_NAME='refunds' THEN
   IF OLD.status='requested' THEN allowed:=ARRAY['approved','rejected'];
   ELSIF OLD.status='approved' THEN allowed:=ARRAY['processing','completed','failed'];
   ELSIF OLD.status='processing' THEN allowed:=ARRAY['completed','failed']; END IF;
 ELSIF TG_TABLE_NAME IN ('products','pattern_releases') THEN
   IF OLD.status='draft' THEN allowed:=ARRAY['published','archived'];
   ELSIF OLD.status='published' THEN allowed:=ARRAY['archived']; END IF;
 ELSIF TG_TABLE_NAME='carts' THEN
   IF OLD.status='active' THEN allowed:=ARRAY['converted','expired','abandoned']; END IF;
 ELSE RETURN NEW;
 END IF;
 IF allowed IS NULL OR NOT NEW.status=ANY(allowed) THEN
 RAISE EXCEPTION 'Invalid % status transition: % -> %', TG_TABLE_NAME,OLD.status,NEW.status USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;

CREATE FUNCTION v2_product_check() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE pid bigint; k text; n integer;
BEGIN
 IF TG_TABLE_NAME='products' THEN pid:=NEW.id; ELSE pid:=COALESCE(NEW.product_id,OLD.product_id); END IF;
 SELECT kind INTO k FROM products WHERE id=pid FOR UPDATE;
 IF NOT FOUND THEN RETURN NULL; END IF;
 SELECT (SELECT count(*) FROM courses WHERE product_id=pid)+(SELECT count(*) FROM patterns WHERE product_id=pid)+(SELECT count(*) FROM bundles WHERE product_id=pid) INTO n;
 IF n<>1 OR (k='course' AND NOT EXISTS(SELECT 1 FROM courses WHERE product_id=pid))
 OR (k='pattern' AND NOT EXISTS(SELECT 1 FROM patterns WHERE product_id=pid))
 OR (k='bundle' AND NOT EXISTS(SELECT 1 FROM bundles WHERE product_id=pid))
 THEN RAISE EXCEPTION 'Product specialization mismatch' USING ERRCODE='23514'; END IF;
 RETURN NULL;
END $$;

CREATE FUNCTION v2_access_check(eid bigint) RETURNS void LANGUAGE plpgsql AS $$
DECLARE e entitlements;
BEGIN
 SELECT * INTO e FROM entitlements WHERE id=eid FOR UPDATE;
 IF NOT FOUND THEN RETURN; END IF;
 IF (SELECT kind FROM products WHERE id=e.product_id) NOT IN ('course','pattern')
 OR (e.status='active')<>EXISTS(SELECT 1 FROM entitlement_grants WHERE entitlement_id=eid AND status='active')
 THEN RAISE EXCEPTION 'Entitlement must reflect active grants' USING ERRCODE='23514'; END IF;
 IF EXISTS(SELECT 1 FROM entitlement_grants g JOIN order_items oi ON oi.id=g.order_item_id JOIN orders o ON o.id=oi.order_id
   WHERE g.entitlement_id=eid AND (o.user_id<>e.user_id OR o.status<>'paid' OR
   (oi.product_id<>e.product_id AND NOT EXISTS(SELECT 1 FROM bundle_purchase_snapshots s WHERE s.order_item_id=oi.id AND s.product_id=e.product_id))))
 THEN RAISE EXCEPTION 'Invalid purchase grant source' USING ERRCODE='23514'; END IF;
 IF EXISTS(SELECT 1 FROM entitlement_grants g JOIN order_items oi ON oi.id=g.order_item_id WHERE g.entitlement_id=eid AND g.status='active'
   AND oi.final_amount>0 AND (SELECT COALESCE(sum(ri.amount),0) FROM refund_items ri JOIN refunds rf ON rf.id=ri.refund_id WHERE ri.order_item_id=oi.id AND rf.status='completed')>=oi.final_amount)
 THEN RAISE EXCEPTION 'Fully refunded item still grants access' USING ERRCODE='23514'; END IF;
END $$;

CREATE FUNCTION v2_access_deferred() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF TG_TABLE_NAME='entitlements' THEN PERFORM v2_access_check(COALESCE(NEW.id,OLD.id));
 ELSE PERFORM v2_access_check(COALESCE(NEW.entitlement_id,OLD.entitlement_id)); END IF;
 RETURN NULL;
END $$;

CREATE FUNCTION v2_relation_guard() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE oid bigint; par bigint;
BEGIN
 IF TG_TABLE_NAME='bundle_items' THEN
   IF (SELECT kind FROM products WHERE id=NEW.product_id) NOT IN ('course','pattern') THEN RAISE EXCEPTION 'Nested bundles forbidden' USING ERRCODE='23514'; END IF;
 ELSIF TG_TABLE_NAME='bundle_purchase_snapshots' THEN
   SELECT order_id INTO oid FROM order_items WHERE id=NEW.order_item_id;
   PERFORM 1 FROM orders WHERE id=oid AND status<>'paid' FOR UPDATE;
   IF NOT FOUND OR NOT EXISTS(SELECT 1 FROM order_items oi JOIN bundles b ON b.product_id=oi.product_id JOIN bundle_items bi ON bi.bundle_id=b.id WHERE oi.id=NEW.order_item_id AND bi.product_id=NEW.product_id AND bi.position=NEW.position)
   OR NOT EXISTS(SELECT 1 FROM products WHERE id=NEW.product_id AND kind=NEW.product_kind AND title=NEW.product_title)
   THEN RAISE EXCEPTION 'Invalid bundle snapshot' USING ERRCODE='23514'; END IF;
 ELSIF TG_TABLE_NAME='reviews' THEN
   IF NOT EXISTS(SELECT 1 FROM entitlements e JOIN entitlement_grants g ON g.entitlement_id=e.id WHERE e.user_id=NEW.user_id AND e.product_id=NEW.product_id AND g.grant_type='purchase') THEN RAISE EXCEPTION 'Review requires purchaser' USING ERRCODE='23514'; END IF;
 ELSIF TG_TABLE_NAME='download_grants' THEN
   IF NOT EXISTS(SELECT 1 FROM entitlements e JOIN patterns p ON p.product_id=e.product_id JOIN pattern_files f ON f.pattern_id=p.id JOIN pattern_releases pr ON pr.id=f.release_id WHERE e.id=NEW.entitlement_id AND e.status='active' AND f.id=NEW.pattern_file_id AND pr.status='published') THEN RAISE EXCEPTION 'Unauthorized file grant' USING ERRCODE='23514'; END IF;
 ELSIF TG_TABLE_NAME='coupon_redemptions' THEN
   PERFORM 1 FROM coupons WHERE id=NEW.coupon_id FOR UPDATE;
   IF NOT EXISTS(SELECT 1 FROM orders WHERE id=NEW.order_id AND user_id=NEW.user_id AND coupon_id=NEW.coupon_id AND status='paid')
   OR EXISTS(SELECT 1 FROM coupons c WHERE c.id=NEW.coupon_id AND ((c.usage_limit IS NOT NULL AND (SELECT count(*) FROM coupon_redemptions WHERE coupon_id=c.id)>=c.usage_limit) OR (c.per_user_limit IS NOT NULL AND (SELECT count(*) FROM coupon_redemptions WHERE coupon_id=c.id AND user_id=NEW.user_id)>=c.per_user_limit)))
   THEN RAISE EXCEPTION 'Invalid coupon redemption or exhausted quota' USING ERRCODE='23514'; END IF;
 ELSIF TG_TABLE_NAME='entitlement_events' THEN
   IF NEW.grant_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM entitlement_grants WHERE id=NEW.grant_id AND entitlement_id=NEW.entitlement_id) THEN RAISE EXCEPTION 'Event grant mismatch' USING ERRCODE='23514'; END IF;
 ELSIF TG_TABLE_NAME='categories' THEN
   -- Serialize hierarchy edits to prevent concurrent cycle creation.
   PERFORM pg_advisory_xact_lock(6721142027);
   IF EXISTS(WITH RECURSIVE parents AS (SELECT id,parent_id FROM categories WHERE id=NEW.parent_id UNION SELECT c.id,c.parent_id FROM categories c JOIN parents p ON c.id=p.parent_id) SELECT 1 FROM parents WHERE id=NEW.id) THEN RAISE EXCEPTION 'Category cycle' USING ERRCODE='23514'; END IF;
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER immutable_history BEFORE UPDATE OR DELETE ON audit_logs FOR EACH ROW EXECUTE FUNCTION v2_immutable();
CREATE TRIGGER immutable_history BEFORE UPDATE OR DELETE ON entitlement_events FOR EACH ROW EXECUTE FUNCTION v2_immutable();
CREATE TRIGGER immutable_history BEFORE UPDATE OR DELETE ON review_moderations FOR EACH ROW EXECUTE FUNCTION v2_immutable();
CREATE TRIGGER immutable_history BEFORE UPDATE OR DELETE ON bundle_purchase_snapshots FOR EACH ROW EXECUTE FUNCTION v2_immutable();
CREATE CONSTRAINT TRIGGER finance_consistency AFTER INSERT OR UPDATE OR DELETE ON orders DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_finance_deferred();
CREATE CONSTRAINT TRIGGER finance_consistency AFTER INSERT OR UPDATE OR DELETE ON order_items DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_finance_deferred();
CREATE CONSTRAINT TRIGGER finance_consistency AFTER INSERT OR UPDATE OR DELETE ON order_discounts DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_finance_deferred();
CREATE CONSTRAINT TRIGGER finance_consistency AFTER INSERT OR UPDATE OR DELETE ON payment_attempts DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_finance_deferred();
CREATE CONSTRAINT TRIGGER finance_consistency AFTER INSERT OR UPDATE OR DELETE ON refunds DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_finance_deferred();
CREATE CONSTRAINT TRIGGER finance_consistency AFTER INSERT OR UPDATE OR DELETE ON refund_items DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_finance_deferred();
CREATE CONSTRAINT TRIGGER finance_consistency AFTER INSERT OR UPDATE OR DELETE ON bundle_purchase_snapshots DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_finance_deferred();
CREATE TRIGGER settled_guard BEFORE UPDATE OR DELETE ON orders FOR EACH ROW EXECUTE FUNCTION v2_settled_guard();
CREATE TRIGGER settled_guard BEFORE UPDATE OR DELETE ON payment_attempts FOR EACH ROW EXECUTE FUNCTION v2_settled_guard();
CREATE TRIGGER settled_guard BEFORE UPDATE OR DELETE ON refunds FOR EACH ROW EXECUTE FUNCTION v2_settled_guard();
CREATE TRIGGER settled_guard BEFORE INSERT OR UPDATE OR DELETE ON order_items FOR EACH ROW EXECUTE FUNCTION v2_settled_guard();
CREATE TRIGGER settled_guard BEFORE INSERT OR UPDATE OR DELETE ON order_discounts FOR EACH ROW EXECUTE FUNCTION v2_settled_guard();
CREATE TRIGGER status_transition BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION v2_transition();
CREATE TRIGGER status_transition BEFORE UPDATE ON payment_attempts FOR EACH ROW EXECUTE FUNCTION v2_transition();
CREATE TRIGGER status_transition BEFORE UPDATE ON refunds FOR EACH ROW EXECUTE FUNCTION v2_transition();
CREATE TRIGGER status_transition BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION v2_transition();
CREATE TRIGGER status_transition BEFORE UPDATE ON pattern_releases FOR EACH ROW EXECUTE FUNCTION v2_transition();
CREATE TRIGGER status_transition BEFORE UPDATE ON carts FOR EACH ROW EXECUTE FUNCTION v2_transition();
CREATE CONSTRAINT TRIGGER specialization AFTER INSERT OR UPDATE OR DELETE ON products DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_product_check();
CREATE CONSTRAINT TRIGGER specialization AFTER INSERT OR UPDATE OR DELETE ON courses DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_product_check();
CREATE CONSTRAINT TRIGGER specialization AFTER INSERT OR UPDATE OR DELETE ON patterns DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_product_check();
CREATE CONSTRAINT TRIGGER specialization AFTER INSERT OR UPDATE OR DELETE ON bundles DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_product_check();
CREATE CONSTRAINT TRIGGER access_consistency AFTER INSERT OR UPDATE OR DELETE ON entitlements DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_access_deferred();
CREATE CONSTRAINT TRIGGER access_consistency AFTER INSERT OR UPDATE OR DELETE ON entitlement_grants DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION v2_access_deferred();
CREATE TRIGGER relation_guard BEFORE INSERT OR UPDATE ON bundle_items FOR EACH ROW EXECUTE FUNCTION v2_relation_guard();
CREATE TRIGGER relation_guard BEFORE INSERT OR UPDATE ON bundle_purchase_snapshots FOR EACH ROW EXECUTE FUNCTION v2_relation_guard();
CREATE TRIGGER relation_guard BEFORE INSERT OR UPDATE ON reviews FOR EACH ROW EXECUTE FUNCTION v2_relation_guard();
CREATE TRIGGER relation_guard BEFORE INSERT OR UPDATE ON download_grants FOR EACH ROW EXECUTE FUNCTION v2_relation_guard();
CREATE TRIGGER relation_guard BEFORE INSERT OR UPDATE ON coupon_redemptions FOR EACH ROW EXECUTE FUNCTION v2_relation_guard();
CREATE TRIGGER relation_guard BEFORE INSERT OR UPDATE ON entitlement_events FOR EACH ROW EXECUTE FUNCTION v2_relation_guard();
CREATE TRIGGER relation_guard BEFORE INSERT OR UPDATE ON categories FOR EACH ROW EXECUTE FUNCTION v2_relation_guard();

DO $$ DECLARE c record; action text; BEGIN
 FOR c IN SELECT con.oid,con.conname,con.conrelid::regclass AS tbl,pg_get_constraintdef(con.oid) AS def,
   (SELECT attname FROM pg_attribute WHERE attrelid=con.conrelid AND attnum=con.conkey[1]) AS col
   FROM pg_constraint con JOIN pg_namespace n ON n.oid=con.connamespace WHERE con.contype='f' AND n.nspname='public'
 LOOP
   action:='RESTRICT';
   IF c.tbl::text IN ('users_groups','users_user_permissions','auth_group_permissions','product_categories','cart_items') AND (c.tbl::text<>'cart_items' OR c.col='cart_id') THEN action:='CASCADE'; END IF;
   IF (c.tbl::text IN ('audit_logs','entitlement_events') AND c.col='actor_id') OR (c.tbl::text='otp_challenges' AND c.col='user_id') THEN action:='SET NULL'; END IF;
   EXECUTE format('ALTER TABLE %s DROP CONSTRAINT %I',c.tbl,c.conname);
   EXECUTE format('ALTER TABLE %s ADD CONSTRAINT %I %s',c.tbl,c.conname,regexp_replace(c.def,'( DEFERRABLE.*| ON DELETE.*)$','')||' ON DELETE '||action||' DEFERRABLE INITIALLY DEFERRED');
 END LOOP;
END $$;
CREATE VIEW daily_sales AS 
WITH captures AS (
 SELECT order_id,sum(amount) AS captured_amount FROM payment_attempts
 WHERE status='succeeded' GROUP BY order_id
), returned AS (
 SELECT p.order_id,sum(r.amount) AS refunded_amount FROM refunds r
 JOIN payment_attempts p ON p.id=r.payment_id WHERE r.status='completed' GROUP BY p.order_id
), facts AS (
 SELECT o.*,COALESCE(c.captured_amount,0) AS captured_amount,
 COALESCE(r.refunded_amount,0) AS refunded_amount
 FROM orders o LEFT JOIN captures c ON c.order_id=o.id LEFT JOIN returned r ON r.order_id=o.id
 WHERE o.status='paid'
)

SELECT (paid_at AT TIME ZONE 'Asia/Tehran')::date AS sale_date,currency,count(*) AS order_count,
sum(subtotal) AS gross_amount,sum(discount_total) AS discount_amount,
sum(payable_total) AS sales_amount,sum(captured_amount) AS captured_amount,
sum(refunded_amount) AS refunded_amount,sum(payable_total-refunded_amount) AS net_sales_amount,
sum(captured_amount-refunded_amount) AS net_cash_amount
FROM facts GROUP BY 1,2;
CREATE VIEW product_sales AS
WITH returned AS (
 SELECT ri.order_item_id,sum(ri.amount) AS amount FROM refund_items ri
 JOIN refunds r ON r.id=ri.refund_id WHERE r.status='completed' GROUP BY ri.order_item_id
)
SELECT oi.product_id,o.currency,count(*) AS units_sold,sum(oi.unit_price) AS gross_amount,
sum(oi.discount_amount) AS discount_amount,sum(oi.final_amount) AS sales_amount,
sum(COALESCE(r.amount,0)) AS refunded_amount,
sum(oi.final_amount-COALESCE(r.amount,0)) AS net_sales_amount
FROM order_items oi JOIN orders o ON o.id=oi.order_id LEFT JOIN returned r ON r.order_item_id=oi.id
WHERE o.status='paid' GROUP BY oi.product_id,o.currency;

CREATE VIEW payment_success_rate AS
SELECT provider,(created_at AT TIME ZONE 'Asia/Tehran')::date AS attempt_date,
count(*) AS total_attempts,count(*) FILTER (WHERE status='succeeded') AS successful_attempts,
count(*) FILTER (WHERE status IN ('succeeded','failed','cancelled')) AS terminal_attempts,
count(*) FILTER (WHERE status='succeeded')::numeric /
NULLIF(count(*) FILTER (WHERE status IN ('succeeded','failed','cancelled')),0) AS success_rate,
COALESCE(sum(amount) FILTER(WHERE status='succeeded'),0) AS captured_amount
FROM payment_attempts GROUP BY 1,2;

CREATE VIEW refund_summary AS
SELECT p.provider,o.currency,r.status,count(*) AS refund_count,sum(r.amount) AS requested_amount,
COALESCE(sum(r.amount) FILTER (WHERE r.status='completed'),0) AS refunded_amount
FROM refunds r JOIN payment_attempts p ON p.id=r.payment_id JOIN orders o ON o.id=p.order_id
GROUP BY p.provider,o.currency,r.status;

CREATE VIEW course_completion AS
WITH lessons_count AS (
 SELECT c.id AS course_id,count(l.id) AS total_lessons FROM courses c
 LEFT JOIN chapters ch ON ch.course_id=c.id AND ch.is_published
 LEFT JOIN lessons l ON l.chapter_id=ch.id AND l.is_published GROUP BY c.id
), progress AS (
 SELECT lp.user_id,ch.course_id,count(*) FILTER(WHERE lp.completed_at IS NOT NULL) AS completed_lessons
 FROM lesson_progress lp JOIN lessons l ON l.id=lp.lesson_id AND l.is_published
 JOIN chapters ch ON ch.id=l.chapter_id AND ch.is_published GROUP BY lp.user_id,ch.course_id
)
SELECT e.user_id,c.id AS course_id,e.status AS access_status,n.total_lessons,
COALESCE(p.completed_lessons,0) AS completed_lessons,
COALESCE(p.completed_lessons,0)::numeric/NULLIF(n.total_lessons,0) AS completion_rate
FROM entitlements e JOIN courses c ON c.product_id=e.product_id
JOIN lessons_count n ON n.course_id=c.id LEFT JOIN progress p ON p.user_id=e.user_id AND p.course_id=c.id;
CREATE VIEW coupon_performance AS 
WITH captures AS (
 SELECT order_id,sum(amount) AS captured_amount FROM payment_attempts
 WHERE status='succeeded' GROUP BY order_id
), returned AS (
 SELECT p.order_id,sum(r.amount) AS refunded_amount FROM refunds r
 JOIN payment_attempts p ON p.id=r.payment_id WHERE r.status='completed' GROUP BY p.order_id
), facts AS (
 SELECT o.*,COALESCE(c.captured_amount,0) AS captured_amount,
 COALESCE(r.refunded_amount,0) AS refunded_amount
 FROM orders o LEFT JOIN captures c ON c.order_id=o.id LEFT JOIN returned r ON r.order_id=o.id
 WHERE o.status='paid'
)

SELECT c.id AS coupon_id,c.code,count(f.id) AS paid_orders,
COALESCE(sum(f.subtotal),0) AS gross_amount,COALESCE(sum(f.discount_total),0) AS discount_amount,
COALESCE(sum(f.payable_total),0) AS sales_amount,COALESCE(sum(f.captured_amount),0) AS captured_amount,
COALESCE(sum(f.refunded_amount),0) AS refunded_amount,
COALESCE(sum(f.payable_total-f.refunded_amount),0) AS net_sales_amount
FROM coupons c LEFT JOIN facts f ON f.coupon_id=c.id GROUP BY c.id,c.code;
'''

class Migration(migrations.Migration):
    dependencies = [('schema_v2', '0001_initial')]
    operations = [migrations.RunSQL(SQL)]
