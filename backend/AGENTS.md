# Backend and database instructions

Read the root [AGENTS.md](../AGENTS.md) and the relevant role reference before changing backend code.

For persistence work, start with [Database references](../agents/database.md). Read only the domain references needed for the change.

- `config.settings` and the routed `accounts`, `courses`, `patterns`, and `commerce` apps implement the legacy API database.
- `schema_v2.settings` and `schema_v2` implement an isolated, incompatible database with no API cutover. Do not mix their users, tables, migrations, or permissions.
- The recorded local V2 schema organization moved tables out of `public`; current V2 Django models, migration discovery, and management commands still assume unqualified/public relations. Do not run them against that organized database until integration is implemented and verified.
- Treat models, applied migrations, raw SQL triggers, and transactional services together as the database contract. ORM validation alone does not describe all constraints.
- Do not access credentials, environment secret files, row exports, or database dumps to investigate schema. Do not change production data.
- Keep changes scoped; append migrations for new schema changes and preserve immutable financial and audit history.
