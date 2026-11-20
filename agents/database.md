# Database reference index

These are reference files, not activated agents. Reviewed against repository source on 2026-11-19. No database connection, secret file, or production data was used. They document implemented behavior and recorded local operations; they do not certify the current live database.

## Read by task

| Task | Reference |
| --- | --- |
| Database identities, physical schemas, relationships, source authority | [Architecture and schema map](database/architecture.md) |
| Every V2 model field, model constraint, and explicit index | [V2 data dictionary](database/v2-dictionary.md) |
| Catalog, prices, checkout, payments, refunds, access, review rules | [Integrity and business rules](database/rules.md) |
| Authentication, database privileges, RBAC, protected data | [Security and permissions](database/security.md) |
| Financial and learning report definitions | [Analytics](database/analytics.md) |
| Migration boundaries, seed behavior, checks, maintenance | [Operations](database/operations.md) |
| Legacy API models and their separate behavior | [Legacy boundary](database/legacy.md), [legacy data dictionary](database/legacy-dictionary.md) |

## Source authority and maintenance

- Current code defines repository behavior: [V2 models](../backend/schema_v2/models.py), [migrations](../backend/schema_v2/migrations/), [services](../backend/schema_v2/services.py), and [tests](../backend/schema_v2/tests.py). Tests show coverage, not proof that this session ran them.
- [Schema decisions](../prompt-files/data-base/schema-decisions.md) record earlier authorized design choices. The referenced schema PDF and PRD/Stitch sources are not supplied here; request them for new requirement decisions.
- [Schema organization](../prompt-files/data-base/schema-organization.md) records a completed local database-only move; [its script](../prompt-files/data-base/organize_schemas.py) defines the mapping and verification. Historical row counts and verification results belong to that operation, not a current-state guarantee.
- Follow parent instructions and existing backend/architect roles. Do not infer unimplemented requirements from these references. Flag contradictions between source, recorded operations, and requested changes.
- When schema or rules change, update the relevant dictionary, rule, security, report, and operations pages together. Keep historical migrations and operation records intact.

## Critical compatibility boundary

The legacy API database, fresh V2 migration layout, and organized local V2 layout are distinct. Current Django code does not integrate the organized layout. Do not run a command merely because an older document lists it as a normal next step. Read the operations reference first.
