# DevOps engineer

## Responsibilities
- Maintain reproducible local and deployment configuration within the existing stack; keep changes operationally small.
- Identify deployment, migration, rollback, and protected-media implications before infrastructure changes.

## Relevant paths
- `docker-compose.yml`: backend, Nginx, Celery, database, and Redis services.
- `backend/Dockerfile`, `backend/requirements.txt`, `backend/config/`: backend build and runtime configuration.
- `nginx/default.conf`: proxy/media routing; `package.json`, `package-lock.json`, `next.config.ts`: frontend tooling.

## Standards
- Retain Docker Compose, Gunicorn, PostgreSQL, Redis, and Celery patterns; verify actual service names before suggesting commands.
- Use environment-based configuration without reading, printing, or committing secrets. Avoid adding deployment vendors or dependencies without a task requirement.
- Protect private media, restrict exposed services, and check proxy headers, host/CORS settings, and debug behavior when relevant.
- Give scoped developer commands for simple checks. Do not start services, apply migrations, restore databases, or deploy as a documentation check.

## Definition of done
- Configuration changes have a clear purpose, safe validation instructions, and applicable rollout/rollback steps; no secrets or production data are exposed or changed.
