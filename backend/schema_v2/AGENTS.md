# Schema V2 instructions

Use [Database references](../../agents/database.md), especially the V2 dictionary, integrity rules, security, and operations references. Parent backend and root instructions apply.

This app is a database implementation, not the backend used by the legacy API routes. Use `schema_v2.settings` only with an explicitly isolated database. Never switch the legacy API settings to V2 as an incidental change.

The repository records a local database organization into `entity`, `profiles`, `transactions`, `events`, `security`, and `analytics`. This app still uses unqualified `db_table` values, and its commands query `public`. Migration discovery also needs integration because `django_migrations` moved to `events`. Do not run migration, seed, validation, or role provisioning commands against the organized database as currently written.

For a database change:

1. Inspect the affected model, migrations `0001` through `0004`, service, and relevant tests. Inspect `prompt-files/data-base/organize_schemas.py` when schema qualification is affected.
2. Preserve PostgreSQL constraints, deferred commit checks, lock ordering, purchase snapshots, and immutable history. Do not disable triggers to make a write pass.
3. Create an additive migration; do not edit frozen historical SQL as a repair strategy. The schema organization script is a one-time operation and rejects repeat execution.
4. Keep model permissions distinct from database privileges and object ownership. No V2 endpoints currently enforce row-level API access.
5. Update the affected database reference and validate on a disposable PostgreSQL database with the appropriate layout. State checks actually run and unresolved integration limits.
