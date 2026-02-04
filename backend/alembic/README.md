# Alembic Database Migrations

This directory contains database migration scripts managed by [Alembic](https://alembic.sqlalchemy.org/), the database migration tool for SQLAlchemy.

## Overview

Alembic manages the evolution of your database schema over time. It tracks changes in version files and provides commands to upgrade or downgrade your database to specific versions.

## Prerequisites

Before running migrations, ensure you have:

1. PostgreSQL database running (local or remote)
2. `DATABASE_URL` environment variable configured in `.env`:
   ```bash
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
   ```
3. Dependencies installed:
   ```bash
   uv sync --all-extras
   ```

## Configuration

- **alembic.ini**: Main Alembic configuration file
- **alembic/env.py**: Environment setup with async PostgreSQL support
- **alembic/versions/**: Directory containing migration version files

## Common Commands

All commands should be run from the `backend/` directory.

### View Current Version

Check which migration version the database is currently at:

```bash
uv run alembic current
```

### View Migration History

Display all available migrations:

```bash
uv run alembic history --verbose
```

### Upgrade Database

Apply all pending migrations to the latest version:

```bash
uv run alembic upgrade head
```

Upgrade to a specific revision:

```bash
uv run alembic upgrade <revision_id>
```

Upgrade one version forward:

```bash
uv run alembic upgrade +1
```

### Downgrade Database

Rollback the last migration:

```bash
uv run alembic downgrade -1
```

Downgrade to a specific revision:

```bash
uv run alembic downgrade <revision_id>
```

Rollback all migrations (return to empty database):

```bash
uv run alembic downgrade base
```

### Create New Migration

Generate a new migration file automatically by detecting model changes:

```bash
uv run alembic revision --autogenerate -m "Description of changes"
```

Create an empty migration file for manual editing:

```bash
uv run alembic revision -m "Description of changes"
```

### Show SQL Without Executing

Preview the SQL that would be executed without applying it:

```bash
uv run alembic upgrade head --sql
```

```bash
uv run alembic downgrade -1 --sql
```

## Migration Files

### Current Migrations

- **001_initial_schema.py**: Creates initial `sessions` and `messages` tables with all indexes and constraints

### Migration File Structure

Each migration file contains:

- **revision**: Unique identifier for this migration
- **down_revision**: Parent migration (creates a linked chain)
- **upgrade()**: Function to apply changes (e.g., CREATE TABLE)
- **downgrade()**: Function to revert changes (e.g., DROP TABLE)

Example:

```python
def upgrade() -> None:
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=True),
        # ... more columns
    )

def downgrade() -> None:
    op.drop_table('sessions')
```

## Best Practices

### 1. Always Test Migrations

Test migrations in a development environment before applying to production:

```bash
# Create a test database
createdb test_db

# Export test DATABASE_URL
export DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/test_db

# Run migrations
uv run alembic upgrade head

# Verify schema
psql test_db -c "\dt"

# Test rollback
uv run alembic downgrade -1
```

### 2. Review Auto-Generated Migrations

Always review migrations created with `--autogenerate` before applying:

- Check column types are correct
- Verify indexes and constraints
- Ensure foreign keys have proper `ondelete` behavior
- Add data migrations if needed

### 3. Keep Migrations Small

Create focused migrations that do one thing well. Split large schema changes into multiple migrations.

### 4. Never Edit Applied Migrations

Once a migration has been applied to production, create a new migration to make further changes instead of editing the existing one.

### 5. Backup Before Production Migrations

Always backup your production database before running migrations:

```bash
pg_dump -h hostname -U username -d dbname > backup_$(date +%Y%m%d_%H%M%S).sql
```

## Troubleshooting

### Migration Out of Sync

If your database and migration history are out of sync:

```bash
# Check current version
uv run alembic current

# Stamp database with current revision (use with caution)
uv run alembic stamp head
```

### Reset Database (Development Only)

To completely reset your development database:

```bash
# Drop all tables
uv run alembic downgrade base

# Recreate schema
uv run alembic upgrade head
```

Or using SQL:

```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO public;
```

Then run migrations:

```bash
uv run alembic upgrade head
```

### Connection Errors

If you get connection errors:

1. Verify `DATABASE_URL` is set correctly:
   ```bash
   echo $DATABASE_URL
   ```

2. Test PostgreSQL connection:
   ```bash
   psql "$DATABASE_URL"
   ```

3. Ensure PostgreSQL is running:
   ```bash
   pg_isready -h localhost
   ```

## Integration with Application

The application uses these models defined in `src/database/models.py`:

- **SessionModel**: Stores user chat sessions
- **MessageModel**: Stores individual messages within sessions

Both models inherit from `Base` (SQLAlchemy DeclarativeBase), which provides the metadata used by Alembic for auto-generating migrations.

## Async Support

This setup uses **asyncpg** driver for async PostgreSQL operations:

- Connection URL format: `postgresql+asyncpg://user:pass@host:port/db`
- Migrations run asynchronously via `async_engine_from_config`
- Compatible with FastAPI's async endpoints

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 001_initial_schema | 2026-02-04 | Initial schema with sessions and messages tables |

---

For more information about the project structure, see the main [README.md](../README.md) and [CLAUDE.md](../CLAUDE.md) files.
