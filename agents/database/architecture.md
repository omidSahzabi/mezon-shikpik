# Database architecture and schema map

## Three layouts to distinguish

| Layout | Code and settings | Meaning |
| --- | --- | --- |
| Legacy API | `backend/config/settings.py`; `AUTH_USER_MODEL=accounts.User` | Existing routes under `backend/config/urls.py` use accounts, courses, patterns, commerce, and adminpanel. |
| Fresh isolated V2 | `backend/schema_v2/settings.py`; `AUTH_USER_MODEL=schema_v2.User` | PostgreSQL database `mezon_lms`; default local port 55432; auth/contenttypes/schema_v2 only; migrations create unqualified relations in the original public layout. No API cutover. |
| Organized local V2 | `prompt-files/data-base/organize_schemas.py` | Recorded 2026-11-15 database-only move; same relation identities and data, new namespaces; Django integration deferred. |

V2 uses PostgreSQL-specific composite keys, deferred constraint triggers, range exclusion, and SQL functions. SQLite is not a substitute for integrity validation. Redis/Celery support the broader backend and are not relational table schemas.

## Complete organized table map

The mapping contains 50 tables: 43 V2 model tables and seven framework/authentication tables, including user permission junctions. `analytics` contains six views. Counts describe the mapping in source, not a new live inventory.

| Schema | Tables |
| --- | --- |
| `entity` (10) | `users`, `auth_group`, `products`, `categories`, `courses`, `lessons`, `patterns`, `bundles`, `promotions`, `coupons` |
| `profiles` (15) | `user_profiles`, `staff_profiles`, `instructor_profiles`, `product_categories`, `chapters`, `lesson_assets`, `pattern_variants`, `pattern_releases`, `pattern_files`, `bundle_items`, `promotion_products`, `entitlements`, `entitlement_grants`, `lesson_progress`, `reviews` |
| `transactions` (10) | `carts`, `cart_items`, `orders`, `order_items`, `order_discounts`, `product_prices`, `coupon_redemptions`, `payment_attempts`, `refunds`, `refund_items` |
| `events` (6) | `audit_logs`, `entitlement_events`, `payment_events`, `review_moderations`, `bundle_purchase_snapshots`, `django_migrations` |
| `security` (9) | `auth_permission`, `auth_group_permissions`, `users_groups`, `users_user_permissions`, `otp_challenges`, `auth_sessions`, `download_grants`, `idempotency_keys`, `django_content_type` |

`public` retains `btree_gist` infrastructure and the 16 shared `v2_*` helper functions; no mapped tables or report views remain there in the recorded organized layout. Namespace names classify data; they do not automatically grant privileges or make all `events` records immutable.

## Relationship paths

- `users` has optional one-to-one user/staff/instructor profiles; the profile primary key is the user foreign key. Group and direct-permission junctions retain Django auth semantics.
- `products` has exactly one course/pattern/bundle specialization matching its immutable kind. Categories connect through `product_categories`; categories form a cycle-free parent hierarchy.
- `courses -> chapters -> lessons -> lesson_assets`; a course may reference an instructor profile. User progress references a lesson, not a product.
- `patterns -> pattern_variants` and `pattern_releases -> pattern_files`; each file also references its pattern and optionally a variant of that same pattern.
- `bundles -> bundle_items -> products`; only course/pattern components are allowed. Purchase-time component records live in `bundle_purchase_snapshots`, independent of future composition.
- Products have effective-dated `product_prices`; promotions connect through `promotion_products`; coupons refer to a promotion.
- `users -> carts -> cart_items -> products`; `users -> orders -> order_items -> products`. Orders optionally reference coupons; discounts store order/item allocations and offer snapshots.
- `orders -> payment_attempts -> payment_events` and `payment_attempts -> refunds -> refund_items -> order_items`. Coupon redemptions link coupon, user, and paid order.
- `users + products -> entitlements -> entitlement_grants`; purchase grants point to order items, manual grants identify an actor. Entitlement events preserve history. Download grants connect an entitlement and a pattern file.
- Reviews connect a user and product; review moderation records identify a review and moderator. Audit records identify targets by text entity type/id, not a universal foreign key.
- Idempotency resource type/id is also a generic reference; it is not a foreign key guaranteeing the referenced resource exists.

## Physical types and deletion

V2 uses `BigAutoField` for implicit app IDs, explicit composite primary keys for `product_categories`, `bundle_items`, and `promotion_products`, and user-key primary keys for the three profiles. Built-in auth IDs follow installed Django migrations. UUID public IDs exist on users, orders, and payment attempts, with both Python generation and SQL defaults.

Money uses `numeric(14,0)` in IRR; promotion value uses `numeric(14,2)`. Timestamps are timezone-aware; V2 uses `Asia/Tehran` for application/reporting boundaries. JSON fields hold metadata, not a substitute for relational integrity. Operational records inherit database-default timestamps; ORM `auto_now` updates do not imply an automatic SQL update timestamp trigger.

Migration `0002` replaces database foreign keys with explicit deletion actions. Default action is RESTRICT; auth membership/permission junctions and product-category links cascade, cart-item cart links cascade, and nullable OTP user / audit actor / entitlement-event actor links use SET NULL. The raw migration is authoritative for database behavior; ORM `on_delete` declarations alone are incomplete. Immutable-history triggers may further reject an update that a deletion action would otherwise attempt.

Framework-owned `auth_group`, `auth_permission`, `auth_group_permissions`, `django_content_type`, `django_migrations`, `users_groups`, and `users_user_permissions` are included in the map. Consult installed Django auth/contenttypes migrations and `0001_initial.py` for their exact versioned fields and indexes; do not invent parallel role or permission tables.
