# Database operations and verification

## Choose the layout before any command

Read [architecture](architecture.md) first. Legacy `config.settings` must not target V2. Existing V2 models and commands must not target the organized local database until schema-qualified ORM access, migration-recorder discovery, raw SQL, auth junctions, permissions, and command introspection are integrated.

`schema-decisions.md` lists setup commands for the original V2 layout. `schema-organization.md` is a later record that explicitly defers Django integration. Preserve that distinction. Do not rerun organization or rebuild/reset the existing database to resolve it.

## Migration history

| Migration | Responsibility |
| --- | --- |
| `0001_initial` | V2 tables, model fields/checks/uniques/indexes, composite keys, auth dependency, and `btree_gist`. |
| `0002_integrity_and_reports` | Composite foreign keys, financial/access/specialization/relationship/status guards, immutable history, explicit database deletion actions, six report views. |
| `0003_hardening` | UUID/server defaults, hash/phone/revocation checks, completed-refund allocation protection, identity guards, purchase coverage, snapshot and fixed-promotion checks. |
| `0004_purchase_and_promotion_guards` | Required direct-purchase grants, exact bundle composition at payment, fixed-discount checks across linked prices/promotions. |

Append migrations for new behavior. The RunSQL migrations have no reverse SQL; do not assume migrating backward restores a prior state. The namespace move is a separate psycopg2 operation, not a Django migration, and migration records now reside in `events.django_migrations` in the recorded organized layout.

The organization script locks all 50 mapped tables, qualifies 16 helper functions, moves views/tables in one transaction, and verifies identities, ACLs, dependencies, fingerprints, FK integrity, and rolled-back probes. Its checks and historical results are documented in the operation record. Do not execute it as a routine validation command; it rejects an already organized layout.

## Setup and seed boundaries

`compose.schema-v2.yml` defines an isolated local stack with its own database/volume and loopback port. Read the configuration before use without opening secret environment files. Do not reuse legacy or production data/volumes.

`seed_demo` is restricted by database name to `mezon_lms`, serializes through advisory lock `6721142026`, and uses natural keys for idempotence. It creates fictional Persian demo identities/content, gives each of three students a mock paid order containing both courses, and records purchases/reviews/progress. Patterns have three variants and one release with nonexistent placeholder storage keys. It calls no real gateway or SMS provider. Existing passwords are not changed; generated credentials are written only for new accounts to an ignored local credentials destination. Do not read or commit that destination.

`configure_database_role` provisions the restricted runtime role; `validate_demo` asserts expected demo data, RBAC, finance, and privileges. Both rely on original public/unqualified names. Neither is a general health check for the organized layout or arbitrary non-demo data.

## Scoped verification commands for developers

The following are examples only for a deliberately disposable PostgreSQL instance with the original public V2 layout and the settings/environment already configured. They are not instructions to run against the existing organized database. The test command requires a separate test database and an identity allowed to create it; verify the target before running.

```powershell
# From backend/, after configuring isolated V2 environment variables.
python manage.py check --settings=schema_v2.settings
python manage.py makemigrations schema_v2 --check --dry-run --settings=schema_v2.settings
python manage.py test schema_v2 --settings=schema_v2.settings
```

These checks do not fix namespace integration or prove compatibility with the organized layout. Schema changes should also be reviewed for raw SQL checks not represented in model state, lock ordering, query plans on affected paths, and migration/retry behavior.

Existing `TransactionTestCase` coverage includes price overlaps/adjacency, immutable financial snapshots, totals/transitions, pattern ancestry/NULL uniqueness, purchaser reviews, bundle snapshots, refund bounds, independent manual grants, append-only audit, duplicate captures/report totals, fixed discounts, required direct grants, and partial/full refund access. Do not describe that list as exhaustive coverage.

## Documentation maintenance and validation limits

Update dictionaries from actual model declarations, including inherited fields and SQL-only changes. Update the namespace map when an approved new table/view is added; the one-time script's exact 50-table precondition is historical, not a permanent ban on schema evolution. Record whether a statement comes from current source, a historical operation, or a newly executed check.

This documentation task used source inspection and static documentation checks only. No migrations, seed, organization script, test database, or live SQL validation was executed. Python was unavailable through `python` in this shell. Backend integration and runtime validation remain separate work.
