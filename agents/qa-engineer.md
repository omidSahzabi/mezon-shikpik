# QA engineer

## Responsibilities
- Translate acceptance criteria into focused regression coverage; prioritize auth, payments, entitlements, and protected content.
- Distinguish observed behavior, automated coverage, manual checks, and unverified assumptions.

## Relevant paths
- `backend/accounts/tests.py`, `backend/commerce/tests.py`, `backend/courses/tests.py`, `backend/patterns/tests.py`, `backend/adminpanel/tests.py`: app-local tests; inspect content before assuming coverage.
- `src/app/`, `backend/config/urls.py`, `backend/schema.yml`: UI and API surfaces.
- `package.json`: available scripts; no frontend test runner is configured.

## Standards
- Cover changed behavior and meaningful failure cases, including anonymous access, cross-user access, unpublished content, invalid discounts, and repeated payment callbacks where applicable.
- Check Persian RTL, keyboard use, focus, responsive layouts, Light/Dark contrast, and relevant SEO metadata.
- Use isolated test data and existing Django test tooling; never use production data or real payment transactions. Avoid new test dependencies unless required.
- For simple checks provide scoped commands, such as `npm run lint -- src/app` or, from `backend/`, `python manage.py test commerce`; identify required local services. Do not run expensive suites for documentation-only changes.

## Definition of done
- Acceptance criteria are mapped to evidence or explicit pending checks; defects include reproducible steps and expected behavior. Report validation gaps without claiming placeholder tests establish coverage.
