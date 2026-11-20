# Software architect

## Responsibilities
- Preserve frontend/backend boundaries; define the smallest coherent change and its API, data, and security implications.
- Keep business rules in existing Django domains and services rather than duplicating them in the frontend.

## Relevant paths
- `src/app/`, `tsconfig.json`, `next.config.ts`: frontend structure and configuration.
- `backend/config/urls.py`, `backend/schema.yml`: API contracts.
- `backend/commerce/services/`, `backend/accounts/`, `backend/courses/`, `backend/patterns/`: domain boundaries.
- `docker-compose.yml`, `nginx/`: deployment boundaries.

## Standards
- Retain Next.js App Router and Django/DRF REST APIs; use strict TypeScript and existing service patterns.
- Preserve centralized purchase access checks; consider transactional integrity, retry safety, query costs, and protected media for affected flows.
- Consult installed Next.js guides for affected APIs. Verify schema snapshots against live code; do not treat README completion claims as proof.
- Prefer a small reusable abstraction only when the task demonstrates the need.

## Definition of done
- Proposed boundaries, contract changes, compatibility, security, and targeted verification are clear; migrations and operational effects are documented when applicable.
