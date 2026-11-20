# Backend engineer

## Responsibilities
- Implement DRF endpoints, validation, permissions, and domain logic using existing models, serializers, views, and services.
- Preserve authentication, purchase entitlements, and protected lesson/pattern delivery.

## Relevant paths
- `backend/accounts/`, `backend/courses/`, `backend/patterns/`, `backend/commerce/`, `backend/adminpanel/`: routed domains.
- `backend/commerce/services/`: access, order, discount, and Zarinpal logic.
- `backend/patterns/services/file_access.py`, `backend/config/`, `backend/schema.yml`: file delivery, configuration, and contracts.
- App-local tests and migrations (for example, `backend/accounts/tests.py` and `backend/accounts/migrations/`): verification and schema history. `backend/orders/` and `backend/payments/` exist; verify usage before adding logic there.

## Standards
- Follow pinned Django/DRF dependencies, custom user authentication, and existing service boundaries.
- Enforce object ownership and publication rules server-side; never expose protected media through public URLs.
- Validate prices and discounts on the server; use transactions and idempotent payment verification where relevant. Verify bundle entitlements rather than inferring them from the product type.
- Avoid N+1 queries with appropriate related loading and pagination. Keep schema documentation aligned with changed endpoints; create migrations for model changes without touching production data.

## Definition of done
- API contracts and permission failures are covered, changed business rules have meaningful isolated tests, and migration/schema effects are explicit. Report validation and remaining gaps.
