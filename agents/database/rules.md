# V2 integrity and business rules

Sources: `backend/schema_v2/models.py`, migrations `0002_integrity_and_reports.py`, `0003_hardening.py`, `0004_purchase_and_promotion_guards.py`, and `services.py`. Model-level field checks and indexes are listed in the [dictionary](v2-dictionary.md). SQL-only checks below are equally part of the contract.

## Catalog and publication

- Every product must have exactly one specialization matching `course`, `pattern`, or `bundle`, validated at transaction commit. Create the product and specialization in one atomic transaction. Product kind cannot change.
- Product and pattern-release statuses allow `draft -> published`, `draft -> archived`, `published -> archived`. Archived is terminal. These are update transition guards, not a requirement to insert every record as draft.
- Chapter and lesson publication are separate booleans. Do not assume a status trigger validates all publication readiness, file availability, or endpoint visibility.
- Category self-parenting is checked locally; ancestor cycles are checked recursively under advisory transaction lock `6721142027`.
- Chapter positions are unique per course; lesson positions per chapter; lesson-asset positions per lesson; bundle positions per bundle. Check exact nonnegative conditions in the dictionary; not every position-like field has the same CHECK.
- Bundle components can only be courses/patterns. Nested bundles are rejected. File composite foreign keys require release and optional variant to belong to the file's pattern.
- Pattern files are unique on `(release, variant, file_kind)` using NULLS NOT DISTINCT, including the common-file case where variant is NULL. Size must be positive and SHA-256 text must be 64 lowercase hexadecimal characters.

## Prices, promotions, coupons

- Prices are nonnegative and effective over `[valid_from, valid_until)`; NULL end means unbounded. GiST exclusion with `btree_gist` forbids overlapping intervals per product, while adjacent intervals are valid.
- Promotion type is percent/fixed; value is positive, percent is at most 100, and end is after start. Fixed discounts cannot exceed any linked price overlapping the promotion window. Guards cover promotion, product-link, and price writes; the SQL does not filter this check by `is_active`.
- Coupon code uniqueness uses `Upper(code)`; optional global/per-user limits must be positive. A redemption must match the paid order's user and coupon and fit usage quotas; its guard locks the coupon row.
- SQL snapshot/totals validation does not implement a full checkout offer engine. Stacking, percentage rounding, promotion eligibility, and live payment/SMS orchestration must not be invented from these tables.

## Carts and order snapshots

- At most one active cart per user; each product appears once per cart. V2 has no cart-item or order-item quantity field.
- Cart transitions: `active -> converted/expired/abandoned`. Order transitions: `pending -> paid/cancelled/expired`. Paid orders remain paid after refunds.
- Order currency is IRR. All totals are nonnegative; `payable_total = subtotal - discount_total`. Each item has `final_amount = unit_price - discount_amount` and one product per order.
- At commit, order subtotal/discount/payable totals equal sums of item unit prices/discounts/final amounts. Order discount total also equals the sum of discount rows. An item-linked discount must belong to the same order via composite FK. These checks do not independently prove a snapshot used the current price schedule or a valid promotion.
- Item insertion checks current product title/kind against the snapshot. Subsequent catalog edits do not rewrite purchased financial snapshots.
- Paid orders reject changes/deletion; identical-value SQL order updates are permitted by the settled guard, but normal ORM timestamp changes can make the row distinct. Paid item and discount snapshots reject insertion/update/deletion.
- Identity guards prevent changing `id` and columns ending `_id` on orders, order items/discounts, payments, refunds/allocations, entitlements/grants, courses, patterns, bundles, pattern variants/releases/files. This also covers fields such as `public_id`; it is not a global rule on every table.

## Bundle settlement and grants

`snapshot_bundle(item)` locks the order and component rows, requires a pending bundle item, and creates missing immutable component snapshots. It does not remove stale snapshots or reconcile later composition changes. At payment, snapshots must exactly match current component product/position pairs; empty bundle purchases are rejected at commit.

Settlement must occur in one outer atomic transaction: create financial snapshots, snapshot bundle composition, record the matching captured payment, mark the order paid with `paid_at`, and invoke `grant_purchase` for its items before commit. Do not treat each helper's own atomic block as sufficient for the entire flow.

Paid direct course/pattern items require a matching purchase grant; paid bundle components require grants for all snapshots. Purchase access follows immutable snapshots, so later bundle edits do not alter earlier ownership.

## Payments, refunds, and balances

- Payment transitions: `initiated -> pending/succeeded/failed/cancelled`; `pending -> succeeded/failed/cancelled`. Same-status updates otherwise pass transition checks, subject to immutability.
- Every succeeded attempt must match its order payable total and have `verified_at`; a paid order requires at least one such attempt. Unique attempt idempotency keys and provider+authority/reference uniqueness guard duplicate identifiers, not duplicate captured cash.
- Multiple succeeded attempts are allowed and remain visible as separate captures. Succeeded attempts reject UPDATE and DELETE, including identical-value updates. A succeeded attempt alone does not implement gateway verification or automatically settle an order.
- Payment events are unique by `(payment, event_key)` and have a mutable `processed_at`. They are not covered by the append-only history trigger.
- Refund transitions: `requested -> approved/rejected`; `approved -> processing/completed/failed`; `processing -> completed/failed`. Completion requires `completed_at`; non-NULL provider references are unique.
- Every refund, including requested/failed/rejected, must target a succeeded attempt and have allocations summing to its positive amount. Every allocation must reference an item of that payment's order.
- All refunds except failed/rejected reserve balance. Reserved amounts cannot exceed the capture per attempt or final amount per order item. Duplicate captures do not increase an item's refundable sales allocation.
- Completed refunds and their allocations are immutable. Parent order locks serialize finance consistency checks.
- `complete_refund` requires an active actor with `schema_v2.change_refund`, locks order before refund, accepts approved/processing states, sets completion/provider/approver fields, and appends audit history. Repeated calls for an already completed refund return it after permission checking.
- Partial completed refunds preserve purchase access. Once completed allocations reach an item's final amount, the service revokes that item's active grants and records events. It revokes an entitlement only when no independent active grant remains. For bundle items this affects grants to included products. The SQL full-refund access check is limited to positive-final-amount items; do not infer special zero-price refund policy.

## Entitlements, downloads, learning, and reviews

- One entitlement per `(user, product)`, only for course/pattern products. Its status is active exactly when at least one active grant exists. Revoked status and non-NULL `revoked_at` must agree for entitlements and grants.
- Purchase grants need an order item on a paid order owned by the entitlement user, matching the product directly or through a bundle snapshot. Each non-NULL `(entitlement, order_item)` pair is unique. Manual grants require no order item and an actor.
- `grant_purchase` locks the order and entitlement, creates missing purchase grants, activates access, and writes events for newly created grants. Existing revoked grants are not automatically reactivated by retrying it.
- `grant_manual` requires an active actor with `schema_v2.grant_manual_access` and a nonblank reason, then creates a grant and entitlement/audit events atomically. The database grant-source CHECK alone does not enforce that actor's permission or a reason; use the service.
- Download-grant writes require active access to the file's pattern and a published release; expiry must follow creation. Token hashes must be unique and match lowercase 64-hex format. Expiry, one-time consumption, current ownership at redemption, and private file delivery still need runtime enforcement; V2 provides no download endpoint.
- Progress is unique per user/lesson with a nonnegative last position. The model does not itself require ownership, cap progress to lesson duration, or validate completed timestamps.
- Reviews are unique per user/product, rating 1..5, status pending/approved/rejected. Writes require a purchase grant, not just a manual grant. The purchaser check does not require the grant still be active. Moderation records are separate history; automatic recording of every review change is not enforced by these triggers.
- Audit logs, entitlement events, review moderations, and bundle purchase snapshots reject UPDATE and DELETE. An entitlement event's optional grant must belong to its entitlement.

## Trigger inventory and timing

The migrations define 16 helpers: `v2_immutable`, `v2_order_check`, `v2_finance_deferred`, `v2_settled_guard`, `v2_transition`, `v2_product_check`, `v2_access_check`, `v2_access_deferred`, `v2_relation_guard`, `v2_refund_allocation_guard`, `v2_identity_guard`, `v2_purchase_coverage`, `v2_catalog_guard`, `v2_purchase_complete`, `v2_bundle_composition_at_payment`, `v2_fixed_discount_check`.

Finance, specialization, access consistency, purchase coverage/completion, and fixed-discount constraint triggers are initially deferred. Other guards run during statements. A successful `save()` can still fail on outer transaction commit; tests must exercise that boundary. The organization script qualifies business table/helper references in these functions and fixes their local search path without changing invoker security.
