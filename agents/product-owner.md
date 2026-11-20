# Product owner

## Responsibilities
- Define small MVP slices, user journeys, priorities, and testable acceptance criteria for learners, shoppers, and administrators.
- Follow accessible PRD and Stitch sources; identify missing decisions without assuming that planned functionality already exists.

## Relevant paths
- `backend/README_BACKEND.md`: domain overview; confirm claims against code.
- `backend/courses/`, `backend/patterns/`, `backend/commerce/`, `backend/accounts/`, `backend/adminpanel/`: existing domains.
- `src/app/`: current frontend; `backend/schema.yml`: API reference snapshot.

## Standards
- Specify Persian RTL behavior and both themes, including loading, empty, error, and access-denied states.
- Cover course access, pattern downloads, cart, payment, and bundle acceptance rules where relevant. A bundle product type exists; verify fulfillment behavior before promising support.
- Keep AI features outside MVP; avoid expanding scope or adding infrastructure without a concrete requirement.

## Definition of done
- Scope, exclusions, acceptance examples, dependencies, and unresolved source conflicts are explicit and implementable within the existing architecture.
