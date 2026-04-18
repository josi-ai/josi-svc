---
description: How to generate and apply Alembic database migrations for the Josi backend
---
// turbo-all

# Database Migrations Workflow

## When to Use
Anytime a **new column, table, or model change** is made to any SQLModel/SQLAlchemy model in `src/josi/models/`, a migration MUST be generated.

## Prerequisites
- The dev server must be running: `josi redock up dev --local` (see `/dev-server` workflow)
- The `josi-api` container must be up and healthy

## Step 1: Generate the Migration

```bash
docker compose exec api alembic revision --autogenerate -m "<descriptive_message>"
```

Example:
```bash
docker compose exec api alembic revision --autogenerate -m "add_language_preference_to_users"
```

## Step 2: Review and Fix the Generated Migration

The generated file will be at `src/alembic/versions/<hash>_<message>.py`.

> [!WARNING]
> **Known Issue**: Alembic autogenerate with SQLModel often produces `sqlmodel.sql.sqltypes.AutoString()` without importing `sqlmodel`. You MUST fix this:
> - Replace `sqlmodel.sql.sqltypes.AutoString()` → `sa.String()`
> - Or add `import sqlmodel` to the imports

## Step 3: Apply the Migration

```bash
docker compose exec api alembic upgrade head
```

## Auto-Migration on Startup

The API container has `AUTO_DB_MIGRATION=True` in `docker-compose.yml`. This means `alembic upgrade head` runs automatically on every container startup via the FastAPI lifespan handler in `src/josi/main.py`.

So once the migration file exists in `src/alembic/versions/`, it will be applied automatically on the next `josi redock up dev --local`.

## Important Notes
- **Always generate migrations** after modifying models — the auto-migration only *applies* existing migrations, it does NOT detect model drift
- The migration files are volume-mounted into the container, so edits to local files in `src/alembic/versions/` are immediately available inside the container
- To check current migration status: `docker compose exec api alembic current`
- To see migration history: `docker compose exec api alembic history`
