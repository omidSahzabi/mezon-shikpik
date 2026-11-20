# Schema V2 implementation decisions

The seven-page `Mezon_Shik_Pik_Database_Schema_v2.pdf` is authoritative. The owner
authorized resolution of ambiguities on 14 November 2026.

## Isolation and compatibility

The legacy apps implement an incompatible, earlier schema. V2 uses the
`schema_v2` Django app and `schema_v2.settings`, with Django's standard authentication,
Groups, Permissions and content types. It is an isolated database implementation,
not an API cutover. Legacy APIs and settings remain unchanged and must not be
pointed at V2 without a separate integration project. No legacy tables are created
in `mezon_lms`. Use `docker compose -f compose.schema-v2.yml` for this stack.
The dedicated Compose project, volume and loopback port 55432 do not reuse the
existing PostgreSQL container, databases, or volumes.

`mezon_owner` is a local bootstrap administrator and migration identity;
`mezon_app` is a non-owner runtime login without role/database creation or DDL.
Only the former is used by the migration runner. Secrets are local and ignored.
The build context excludes environment files. Passwords use Argon2id.

## Types and lifecycle

Money is integer IRR in numeric(14,0); promotion values have two fractional digits.
Operational rows receive database timestamp defaults; event-only and composite
join rows receive only the fields specified. Profile primary keys are their user
keys. Django's built-in auth IDs retain Django-managed types for compatibility.
UUIDs use Django UUID generation plus a PostgreSQL default. Hashes use varchar(64)
with an exact 64-character lowercase hexadecimal CHECK, preserving fixed length
without PostgreSQL char padding semantics. Currency uses varchar(3) with an
IRR-only CHECK, preserving the equivalent allowed domain.

Status vocabularies and permitted transitions:

| Entity | Lifecycle |
|---|---|
| Product/release | draft → published → archived; draft → archived |
| Cart | active → converted/expired/abandoned |
| Order | pending → paid/cancelled/expired; paid remains paid after refunds |
| Payment | initiated → pending/succeeded/failed/cancelled; pending → succeeded/failed/cancelled |
| Refund | requested → approved/rejected; approved → processing/completed/failed; processing → completed/failed |
| Access/grant | active/revoked; entitlement derives from active grants |
| Review | pending/approved/rejected; moderation is recorded separately |

Captured payments cannot be changed or deleted; duplicates are separate attempts
with independent unique references, so extra captured cash remains visible.
Paid orders and their financial item/discount snapshots are immutable. Completed
refunds and their allocations are immutable. Audit, entitlement events, review
moderations, and bundle snapshots reject UPDATE and DELETE.

## Purchase snapshots and invariants

`bundle_purchase_snapshots` is the one additional domain table: one immutable row
per purchased order item and included product, with title, kind and position.
Purchase grants reference that snapshot rather than current bundle composition.
Composition changes cannot change existing ownership. Empty bundle purchases and
incomplete bundle grant coverage are rejected at transaction commit.

Deferred database triggers validate order totals against summed item and discount
snapshots, paid payment amounts, refund allocations and balances, specialization,
and access/grant consistency. Parent-row locks serialize financial balance and
grant checks. Foreign keys include database deletion actions, not merely ORM
deletion behavior. Composite foreign keys enforce pattern-file ancestry and
same-order discounts. PostgreSQL 15 NULLS NOT DISTINCT protects common pattern
files. GiST range exclusion prevents overlapping prices, using `[start,end)`.
Category edits use an advisory transaction lock and recursive cycle detection.

All three seeded students purchase both courses in one mock paid order each.
Patterns have three sizes and one release each, with non-existent placeholder
storage keys. No download files, payment gateway calls or SMS are generated.
Seed uses deterministic natural keys, serializes concurrent invocations and never
changes existing account passwords. Credentials are appended only for new users.

## Authorization boundary

Admin has all Django model permissions. Instructor has add/change/view permissions
for educational content. Support has selected read, review moderation and refund
request permissions, but no financial approval permission. Student has no global
model permissions: personal access is determined by ownership. These are model
permissions, not row-level authorization; future APIs must enforce instructor
assignment and personal/support scope. Manual grants require the explicit custom
permission and append audit history. No new endpoints are provided.

## Reporting definitions

The six views are `daily_sales`, `product_sales`, `payment_success_rate`,
`refund_summary`, `course_completion`, and `coupon_performance`.

Gross means item list-price snapshots on paid orders. Sales means gross minus
snapshotted discounts. Captured means all succeeded attempts, including duplicate
charges. Refunded means completed refunds only. Net sales is sales less completed
refunds; net cash is captured less completed refunds. Pending/failed refunds are
not cash movements. Sales days use Asia/Tehran and order paid_at. Refunds attributed
to a sales day restate that cohort; this is not a daily cash-flow ledger.
Product sales use explicit item refund allocations and do not attribute extra
duplicate captures to products. Bundle revenue stays with the sold bundle, with
no invented allocation across its components. All financial views aggregate facts
before joining to prevent multiplicative counting. Payment success rate uses
terminal attempts as denominator, excluding in-flight attempts. Empty denominators
are NULL. Course completion counts currently published lessons in published
chapters per entitled student. Coupon performance counts paid orders and their
snapshots, retaining coupons with zero sales.

## Running

Start `docker compose -f compose.schema-v2.yml up -d db`, then run Django commands
with `docker compose -f compose.schema-v2.yml run --rm django python manage.py`:
`migrate`, `check`, `seed_demo`, `configure_database_role`, and `validate_demo`.
Run tests using `test schema_v2`. The runner uses owner credentials; deployed
application processes must use the restricted runtime identity from the local
credentials file. Default `backend/config/settings.py` still serves legacy APIs.
