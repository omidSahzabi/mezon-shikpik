# V2 security and permissions

Sources: V2 models/services/settings, `management/commands/seed_demo.py`, `configure_database_role.py`, SQL migrations, and schema organization script. These layers serve different purposes; a PostgreSQL login does not represent an end-user role.

## Identity and sensitive values

V2 authenticates by unique phone in E.164 form (`+` followed by 8..15 digits, first digit nonzero). Non-NULL email uniqueness is case-insensitive. Password hashing uses Django's Argon2PasswordHasher (Argon2id per recorded decisions); never store or log plaintext passwords.

OTP challenges store `code_hash`, purpose, expiry, attempts (0..10), and consumption time. Session and download tokens store unique 64-character lowercase hexadecimal hashes. Idempotency request hashes use the same format. These constraints verify representation, not that a caller actually hashed a secure token. Code generation, rate limiting, expiry checks, session limits, replay/consumption, and API authentication are not supplied by V2 tables alone.

Audit JSON, gateway event payloads, device metadata, IPs, phone/email, and storage keys may carry private data. Do not include secrets or raw tokens in logs, fixture exports, documentation, or debugging output. A storage key is not a public download URL. No secret files or database rows are needed for schema documentation.

## Seeded Django roles

These are assignments made by `seed_demo`, not an automatically enforced role hierarchy or PostgreSQL RLS policy.

| Group | Seeded permission scope |
| --- | --- |
| Admin | All Django permissions present when seed runs. Later-created permissions require deliberate assignment. |
| Instructor | `view`, `add`, `change` on course, chapter, lesson, lessonasset, pattern, patternvariant, patternrelease, patternfile; no blanket delete or financial permissions. |
| Support | `view_user`, `view_userprofile`, `view_order`, `view_orderitem`, `view_paymentattempt`, `view_entitlement`, `view_review`, `change_review`, `add_reviewmoderation`, `view_refund`, `add_refund`. |
| Student | No global model permissions; personal access must use ownership and entitlements. |

`schema_v2.grant_manual_access` is a custom permission on EntitlementGrant. `grant_manual` also checks actor activity and reason. Refund completion requires `schema_v2.change_refund`; Support is deliberately not assigned that permission. Staff/profile flags and instructor public visibility are not substitutes for authorization.

Future API integration must enforce instructor assignment, user ownership, support scope, publication, and protected delivery on the backend. Group membership alone does not establish object access. V2 currently has no such endpoints and no implemented database row-level security policy.

## Database identities and privileges

- `mezon_owner` is the isolated local bootstrap/migration identity; use it only for deliberate setup/DDL. Do not expose its credentials to application processes.
- `mezon_app` is the restricted runtime identity: no superuser, database/role creation, or replication privilege. The provisioning code grants connection, schema usage, table DML, and sequence usage/select; four append-only tables receive SELECT/INSERT only. It omits grants on `django_migrations`.
- Analytics views receive SELECT. Shared `v2_*` functions receive EXECUTE; the provisioning command revokes PUBLIC execution on public functions. Function execution does not grant ownership or bypass their invoker-security privileges.
- The recorded organization preserves object ACLs/owners, grants runtime USAGE on destination schemas, grants no schema CREATE, and gives PUBLIC no access to those schemas. It does not change role-wide/database-wide search paths or introduce new RBAC permissions.
- Current role provisioning scans `public` and uses unqualified views/functions. It must be adapted before running against the organized layout. Treat the code as a provisioner for the original layout, not proof of current live ACLs.

Preserve database restrictions and application checks together. Do not grant the runtime role migration ownership, broad schema creation, or history mutation to work around an integration error.
