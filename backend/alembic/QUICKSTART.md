# Alembic Quick Start Guide

Quick reference for getting started with Alembic database migrations.

## Prerequisites

1. **Install dependencies** (from `backend/` directory):
   ```bash
   uv sync --extra api
   ```

2. **Set up PostgreSQL database**:
   - Ensure PostgreSQL is running
   - Create a database (or use existing)
   - Configure `.env` file with database credentials

3. **Configure environment variables** in `.env`:
   ```bash
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=rag_events
   POSTGRES_USER=your_username
   POSTGRES_PASSWORD=your_password
   ```

## Initial Setup (First Time)

### Step 1: Verify Configuration

Check that Alembic can read your configuration:

```bash
cd backend
uv run alembic current
```

Expected output if database is empty:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

### Step 2: Apply Initial Migration

Create the `sessions` and `messages` tables:

```bash
uv run alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial_schema, Initial schema: create sessions and messages tables
```

### Step 3: Verify Tables Created

Connect to PostgreSQL and check tables:

```bash
psql -h localhost -U your_username -d rag_events -c "\dt"
```

You should see:
```
         List of relations
 Schema |   Name   | Type  |  Owner
--------+----------+-------+---------
 public | sessions | table | rag_user
 public | messages | table | rag_user
 public | alembic_version | table | rag_user
```

## Common Workflows

### Check Current Database Version

```bash
uv run alembic current
```

### View Migration History

```bash
uv run alembic history
```

### Apply New Migrations

```bash
# Upgrade to latest version
uv run alembic upgrade head

# Upgrade one version forward
uv run alembic upgrade +1
```

### Rollback Migrations

```bash
# Rollback one version
uv run alembic downgrade -1

# Rollback to beginning (WARNING: drops all tables)
uv run alembic downgrade base
```

### Create New Migration

After modifying models in `src/database/models.py`:

```bash
# Auto-generate migration from model changes
uv run alembic revision --autogenerate -m "Add user_preferences column"

# Create empty migration for manual editing
uv run alembic revision -m "Add custom function"
```

### Preview SQL Without Running

```bash
# See SQL that would be executed
uv run alembic upgrade head --sql

# Save SQL to file
uv run alembic upgrade head --sql > migration.sql
```

## Troubleshooting

### Error: "Can't locate revision identified by..."

The database thinks it's at a different version. Check current version:

```bash
uv run alembic current
```

If necessary, stamp the database with the correct version (use with caution):

```bash
uv run alembic stamp head
```

### Error: "FATAL: password authentication failed"

Check your `.env` file has correct credentials:
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`

Test connection manually:
```bash
psql -h localhost -U your_username -d rag_events
```

### Error: "Target database is not up to date"

Apply pending migrations:
```bash
uv run alembic upgrade head
```

### Starting Fresh (Development Only)

To completely reset the database:

```bash
# Drop all tables
uv run alembic downgrade base

# Recreate from scratch
uv run alembic upgrade head
```

## Database Schema

### Current Tables (v001_initial_schema)

**sessions**
- `id` (UUID, primary key)
- `user_id` (VARCHAR, nullable, indexed)
- `created_at` (TIMESTAMP, default CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP, default CURRENT_TIMESTAMP)
- `metadata` (JSONB, nullable)

**messages**
- `id` (INTEGER, primary key, auto-increment)
- `session_id` (UUID, foreign key to sessions.id, CASCADE DELETE)
- `role` (VARCHAR, CHECK: 'user' or 'assistant')
- `content` (TEXT)
- `created_at` (TIMESTAMP, default CURRENT_TIMESTAMP)
- `sources` (JSONB, nullable)
- `latency_ms` (FLOAT, nullable)
- `top_k` (INTEGER, nullable)
- `query_type` (VARCHAR, nullable)

### Indexes

**sessions**
- `ix_sessions_user_id` on `user_id`
- `ix_sessions_user_created` on `(user_id, created_at)`
- `ix_sessions_created_at` on `created_at`

**messages**
- `ix_messages_session_id` on `session_id`
- `ix_messages_session_created` on `(session_id, created_at)`

## Next Steps

- Review [README.md](./README.md) for detailed documentation
- Check [001_initial_schema.py](./versions/001_initial_schema.py) to see the migration code
- Read [Alembic documentation](https://alembic.sqlalchemy.org/) for advanced features

## Docker Usage

If using Docker Compose, migrations can be run in the container:

```bash
# Run migrations in Docker container
docker-compose exec backend uv run alembic upgrade head

# Or during container startup (add to Dockerfile CMD)
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000"]
```

---

For more information, see the full [Alembic README](./README.md).
