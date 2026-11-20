# Legacy API database boundary

Sources: `backend/accounts`, `courses`, `patterns`, `commerce` models/services/permissions and `config/urls.py`. The [legacy dictionary](legacy-dictionary.md) lists all locally declared model fields, constraints, and explicit indexes. Do not apply V2 status names, price types, tables, roles, or entitlement semantics here.

## Model ownership

| App | Models and relationships |
| --- | --- |
| accounts | User with string `role`; OTPCode; UserSession. Uses `accounts.User` and Django permission mixins. |
| courses | Course -> Chapter -> Lesson; LessonProgress unique per user/lesson. Course/lesson `is_free` flags and direct file fields differ from V2. |
| patterns | Pattern with one file, direct price, and publication flag; no current variant/release models. |
| commerce | Product links optional course/pattern, Discount, one Cart per user, CartItem with quantity, Order, OrderItem with price/quantity snapshots, Purchase, one Payment per order, Wishlist. |
| orders, payments, adminpanel | Their `models.py` files declare no models. Commerce owns the implemented order/payment models; adminpanel provides routed views. |

Legacy app tables use Django's default app/model table names because these models do not set `db_table`. Framework/session/admin tables depend on installed apps and their migrations; this is a source inventory of local domain models, not a verified live catalog.

## Implemented behavior and differences

- User roles are student/admin/support/instructor strings; role choices are not V2 seeded Groups. Admin/support/student permission classes compare the string role. Do not replace them with V2 model permissions incidentally.
- OTPCode stores a code and `is_used`; validity checks unused state and expiry. It does not use V2 `code_hash` or attempt/purpose fields.
- Legacy custom authentication reads `X-Session-Key`, checks session existence/activity/expiry and user blocking, and updates last activity. It does not check user `is_active` in that authentication method. Session cleanup deactivates oldest active sessions above `MAX_SESSIONS=3`; that is application logic, not a database limit.
- AccessService grants free-course access directly, otherwise checks Purchase by product-course relation. Pattern access checks Purchase by product-pattern relation. The separate HasCourseAccess permission always requires an authenticated purchaser; its semantics differ from AccessService's free-course branch. Inspect the affected view before changing access behavior.
- Pattern serving looks up a published pattern and checks purchase access before opening its file as an attachment. Preserve backend authorization and protected delivery.
- Course and pattern prices, product price, order total, payment amount, and item price use PositiveIntegerField. Do not assume the legacy source enforces V2 numeric(14,0), explicit IRR currency, or scheduled prices.
- DiscountService checks exact code lookup, active state, optional start/end bounds, maximum use, and percent in 1..100. Discount amount uses integer floor division. Cart.total_price applies its attached discount directly; it does not perform those eligibility checks itself.
- Atomic OrderService.create_order requires nonempty cart, rejects already purchased products, calculates totals from product prices/quantities and an optional discount, creates a pending order/items/payment, clears cart items and attached discount. This service does not supply V2 deferred totals, immutable records, multiple payment attempts, bundle snapshots, or audited refunds.
- Legacy Purchase and Wishlist are unique per user/product. Model choices and service checks are not equivalent to SQL CHECK constraints. In particular, legacy Product has a bundle type choice without the V2 component/snapshot model or specialization enforcement.
- Order statuses are pending/paid/failed; payment statuses pending/success/failed. Legacy payment views include fake success and verification paths that mark records paid and create purchases without the V2 gateway/integrity contract. They must not be cited as proof of production gateway verification or V2 idempotency.

These are existing implementation limits, not authorization to redesign checkout or security as part of documentation. For any API change, inspect that view, serializer, service, permission, and tests together; this page does not claim to enumerate every endpoint validation rule.
