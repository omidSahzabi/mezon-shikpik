# PostgreSQL schema organization

Executed on 15 November 2026 against the isolated local `mezon_lms` database.
This is a database-only change. No Django models, migrations, settings, APIs,
frontend files, or RBAC definitions were modified.

## Final mapping: all 50 existing tables

| Schema | Tables | Rationale |
|---|---|---|
| `entity` (10) | `users`, `auth_group`, `products`, `categories`, `courses`, `lessons`, `patterns`, `bundles`, `promotions`, `coupons` | Independently identified people, roles, educational/catalog entities, and reusable commercial offers. Promotions and coupons describe offers, rather than individual financial movements. |
| `profiles` (15) | `user_profiles`, `staff_profiles`, `instructor_profiles`, `product_categories`, `chapters`, `lesson_assets`, `pattern_variants`, `pattern_releases`, `pattern_files`, `bundle_items`, `promotion_products`, `entitlements`, `entitlement_grants`, `lesson_progress`, `reviews` | Profiles, dependent content, entity relationships and current user/product state. Chapters organize course content; releases and file metadata describe pattern versions. Entitlements and grants describe durable ownership relationships, rather than authentication credentials. Reviews are current moderated records; their history is separate. |
| `transactions` (10) | `carts`, `cart_items`, `orders`, `order_items`, `order_discounts`, `product_prices`, `coupon_redemptions`, `payment_attempts`, `refunds`, `refund_items` | Purchase workflow, financial amounts and allocations. Effective prices are financial schedules; coupon redemptions are recorded financial uses. |
| `events` (6) | `audit_logs`, `entitlement_events`, `payment_events`, `review_moderations`, `bundle_purchase_snapshots`, `django_migrations` | Append-only history, purchase-time evidence and system execution history. Bundle snapshots are immutable purchase history; migration records are framework execution history, not catalog entities. |
| `security` (9) | `auth_permission`, `auth_group_permissions`, `users_groups`, `users_user_permissions`, `otp_challenges`, `auth_sessions`, `download_grants`, `idempotency_keys`, `django_content_type` | Permissions, role assignments, authentication/access tokens, replay protection and permission resource metadata. Security-sensitive junctions belong here rather than in the general relationship schema. |
| `analytics` (six views; no tables) | `daily_sales`, `product_sales`, `payment_success_rate`, `refund_summary`, `course_completion`, `coupon_performance` | Reporting projections; existing calculations preserved. |
| `public` (no tables or reporting views) | Existing `btree_gist` extension objects and all 16 shared `v2_*` integrity/trigger helper functions | Shared infrastructure only. |

Table names and columns are unchanged. Every table has exactly one destination.
No compatibility tables or views were created in `public`.

## Execution and preservation

The database operation is recorded in `organize_schemas.py` alongside this file.
It uses psycopg2 directly, without Django imports, through the existing Compose
runner's owner credentials. It exports no row data, credentials, password hashes,
or database dumps. Row fingerprints are computed in PostgreSQL and compared in
process; only aggregate verification results are printed.

One transaction acquires an advisory lock and access-exclusive locks on all 50
tables, with a 10-second lock timeout and 120-second statement timeout. It creates
the six destination schemas, then uses `ALTER TABLE ... SET SCHEMA` and
`ALTER VIEW ... SET SCHEMA`. There are no table copies, rebuilds, deletes or
database resets. An unsuccessful validation rolls back the entire operation.

PostgreSQL retains table, index, sequence, constraint, trigger, and view identities.
Owned sequences and indexes move with their tables. Foreign keys and view queries
remain attached by object ID, so cross-schema dependencies continue to resolve.
View definitions now deparse with the appropriate schema-qualified relations.

PL/pgSQL source references need explicit handling: all 16 shared `v2_*` functions
were replaced in place, qualifying table references, row types and helper calls.
String literals, comments and trigger table-name comparisons are preserved.
Each helper has a fixed function-local search path of
`pg_catalog, public, pg_temp`; all business relations use explicit qualification.
Functions remain invoker-security functions. Existing trigger bindings, execution
permissions and owners are unchanged. Extension functions were not replaced.

Existing object ACLs and ownership were compared before/after. Destination
schemas are owned by `mezon_owner`; `PUBLIC` receives no access to them.
`mezon_app` receives schema `USAGE` only, making its existing table, sequence,
view and helper-function privileges effective in the new locations. It receives
no schema `CREATE` privilege. No roles or model permissions were added or changed.
No database-wide or role-wide search path was changed.

## Verification results

- All 50 existing tables accounted for; no tables remain in `public`.
- All 589 existing rows have identical per-table counts and full-row fingerprints.
  This includes authentication, RBAC, framework metadata and demo data.
- All 240 constraints retain their object IDs, keys, expressions, validation and
  deferral flags; all 76 foreign keys were additionally checked against actual
  child/parent rows, including composite keys. No orphans were found.
- All 63 application triggers retain their object IDs, function bindings,
  enabled states, event types and deferral flags. Internal triggers are also
  included in the identity comparison.
- All 44 sequence states, identities, ACLs and owners are unchanged.
- All existing relation/index/view identities, ACLs and owners are unchanged.
- All 1,224 inventoried dependency edges were compared; only schema namespace
  dependency changes were permitted.
- All six analytics views return the same complete result sets as before the move.
- Order and entitlement integrity helper checks pass for every existing record,
  both as owner and as the restricted `mezon_app` role. That role can read all
  six reporting views with the new schema qualification.
- Rolled-back positive update probes exercise deferred product specialization,
  entitlement consistency, review purchaser checks and pricing checks.
- Rolled-back negative probes reject paid-order changes, captured-payment changes,
  audit/event history updates, invalid publication transitions and inconsistent
  order totals. Probe inserts use an explicit temporary ID; sequence counters do
  not advance. No probe data is retained.

The first attempt rolled back because a validation probe used an identical-value
paid-order update, which the preexisting guard correctly permits. The probe was
corrected to attempt an actual order-number change; the full rerun passed and
committed. This did not require changing any business constraint or trigger rule.

## Integration boundary and remaining work

Django integration is deliberately deferred. Existing unqualified model names,
migrations, seed/validation commands and public-only catalog queries are not
updated and must not be run against this reorganized database until a separate
integration task addresses them. The existing Django migration records themselves
are preserved in `events.django_migrations`.

Applications and SQL clients should use explicit names such as `entity.users`,
`transactions.orders`, and `analytics.daily_sales`. Do not rerun the organization
script: it intentionally rejects an already reorganized layout. A future reverse
move can use the same preserved object identities, but no rollback or backend
compatibility layer was applied here. Refresh pgAdmin's database tree to see the
new schemas.
