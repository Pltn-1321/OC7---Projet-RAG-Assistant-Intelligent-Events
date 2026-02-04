# Alembic Installation Summary

This document provides a complete overview of the Alembic migration setup for the RAG Events Assistant backend.

## Installation Date

**Installed**: 2026-02-04

## Files Created

### Configuration Files

1. **backend/alembic.ini**
   - Main Alembic configuration file
   - Configures script location, file templates, logging
   - Includes post-write hooks for Black formatting
   - SQLAlchemy URL is set dynamically from `settings.py`

2. **backend/alembic/script.py.mako**
   - Template for generating new migration files
   - Provides standard structure with upgrade/downgrade functions
   - Used by `alembic revision` command

### Environment Configuration

3. **backend/alembic/env.py**
   - Environment setup with async PostgreSQL support
   - Imports `Base` metadata from `src.database.models`
   - Configures async engine using `asyncpg` driver
   - Supports both offline and online migration modes
   - Automatically loads `DATABASE_URL` from settings

### Migrations

4. **backend/alembic/versions/001_initial_schema.py**
   - Initial migration creating `sessions` and `messages` tables
   - Includes all indexes and constraints
   - Provides upgrade and downgrade functions
   - Revision ID: `001_initial_schema`

### Documentation

5. **backend/alembic/README.md**
   - Comprehensive documentation for Alembic usage
   - Common commands and workflows
   - Best practices and troubleshooting
   - Integration with the application

6. **backend/alembic/QUICKSTART.md**
   - Quick reference guide for getting started
   - Step-by-step setup instructions
   - Common workflows and troubleshooting
   - Database schema reference

7. **backend/alembic/INSTALLATION.md** (this file)
   - Installation summary and overview
   - Architecture details
   - Verification procedures

### Python Packages

8. **backend/alembic/__init__.py**
   - Package marker for alembic directory

9. **backend/alembic/versions/__init__.py**
   - Package marker for versions directory

### Verification Script

10. **backend/scripts/verify_alembic.py**
    - Automated verification script
    - Checks environment variables, database connectivity
    - Verifies Alembic configuration and models
    - Provides diagnostic information

## Updated Files

### Dependencies

**backend/pyproject.toml**
- Added to `[project.optional-dependencies.api]`:
  - `asyncpg>=0.29.0,<1.0.0` - PostgreSQL async driver
  - `sqlalchemy[asyncio]>=2.0.0,<3.0.0` - ORM with async support
  - `alembic>=1.13.0,<2.0.0` - Database migration tool

### Settings

**backend/src/config/settings.py**
- Relaxed PostgreSQL password validator for development
- Already had PostgreSQL configuration variables:
  - `postgres_host`
  - `postgres_port`
  - `postgres_user`
  - `postgres_password`
  - `postgres_db`
  - `postgres_pool_size`
  - `postgres_max_overflow`
- `database_url` property generates asyncpg connection string

### Environment Variables

**.env.example**
- Already contained complete PostgreSQL configuration
- Includes `DATABASE_URL` template
- Provides pgAdmin configuration

## Architecture Overview

### Database Models

Located in `backend/src/database/models.py`:

```python
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

class SessionModel(Base):
    """User chat sessions."""
    __tablename__ = "sessions"
    # Fields: id, user_id, created_at, updated_at, metadata
    # Relationships: messages (one-to-many)

class MessageModel(Base):
    """Chat messages within sessions."""
    __tablename__ = "messages"
    # Fields: id, session_id, role, content, created_at,
    #         sources, latency_ms, top_k, query_type
    # Relationships: session (many-to-one)
```

### Migration Flow

```
User Command (alembic upgrade head)
         ↓
   alembic.ini (configuration)
         ↓
   alembic/env.py (environment setup)
         ↓
   Load Base.metadata from src.database.models
         ↓
   Create AsyncEngine with asyncpg driver
         ↓
   Read DATABASE_URL from settings
         ↓
   Execute migration files in order
         ↓
   Update alembic_version table
```

### Database Connection

Connection URL format:
```
postgresql+asyncpg://user:password@host:port/database
```

Components:
- **Protocol**: `postgresql+asyncpg` (async driver)
- **User**: From `POSTGRES_USER` env var
- **Password**: From `POSTGRES_PASSWORD` env var
- **Host**: From `POSTGRES_HOST` env var (default: localhost)
- **Port**: From `POSTGRES_PORT` env var (default: 5432)
- **Database**: From `POSTGRES_DB` env var (default: rag_events)

## Directory Structure

```
backend/
├── alembic.ini                    # Main configuration
├── alembic/
│   ├── __init__.py               # Package marker
│   ├── env.py                    # Environment setup
│   ├── script.py.mako            # Migration template
│   ├── README.md                 # Full documentation
│   ├── QUICKSTART.md             # Quick reference
│   ├── INSTALLATION.md           # This file
│   └── versions/
│       ├── __init__.py           # Package marker
│       └── 001_initial_schema.py # Initial migration
├── scripts/
│   └── verify_alembic.py         # Verification script
└── src/
    ├── config/
    │   └── settings.py           # Database URL configuration
    └── database/
        ├── __init__.py
        └── models.py             # SQLAlchemy models (Base, SessionModel, MessageModel)
```

## Installation Verification

### Step 1: Install Dependencies

```bash
cd backend
uv sync --extra api
```

This installs:
- SQLAlchemy 2.0+ with async support
- asyncpg PostgreSQL driver
- Alembic migration tool

### Step 2: Configure Environment

Ensure `.env` file exists with PostgreSQL configuration:

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_events
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

### Step 3: Run Verification Script

```bash
uv run python scripts/verify_alembic.py
```

This checks:
- Environment variables are set
- Database connection works
- Alembic configuration files exist
- Models can be imported

### Step 4: Check Alembic Status

```bash
uv run alembic current
```

Should output migration context information without errors.

### Step 5: Apply Initial Migration

```bash
uv run alembic upgrade head
```

Creates `sessions`, `messages`, and `alembic_version` tables.

### Step 6: Verify Tables Created

```bash
psql -h localhost -U your_username -d rag_events -c "\dt"
```

Should show:
- `sessions`
- `messages`
- `alembic_version`

## Common Operations

### View Current Version

```bash
uv run alembic current
```

### View History

```bash
uv run alembic history --verbose
```

### Create New Migration

```bash
# Auto-generate from model changes
uv run alembic revision --autogenerate -m "Add user_preferences"

# Create empty migration
uv run alembic revision -m "Add custom index"
```

### Apply Migrations

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Apply one migration
uv run alembic upgrade +1
```

### Rollback Migrations

```bash
# Rollback one migration
uv run alembic downgrade -1

# Rollback to beginning
uv run alembic downgrade base
```

## Integration with Application

### FastAPI Integration

The application uses these models for session persistence:

```python
from src.database.models import SessionModel, MessageModel

# Create session
session = SessionModel(user_id="user123")

# Add message
message = MessageModel(
    session_id=session.id,
    role="user",
    content="Hello"
)
```

### Async Context

All database operations use async/await:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.config.settings import settings

engine = create_async_engine(settings.database_url)

async with AsyncSession(engine) as session:
    result = await session.execute(select(SessionModel))
    sessions = result.scalars().all()
```

## Testing

### Test Database Connection

```python
import asyncio
import asyncpg
from src.config.settings import settings

async def test():
    conn = await asyncpg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db
    )
    version = await conn.fetchval("SELECT version()")
    print(version)
    await conn.close()

asyncio.run(test())
```

### Test Migration

```bash
# Preview SQL without executing
uv run alembic upgrade head --sql

# Apply to test database
export DATABASE_URL=postgresql+asyncpg://user:pass@localhost/test_db
uv run alembic upgrade head

# Verify
psql test_db -c "\dt"
```

## Maintenance

### Regular Updates

1. After modifying models in `src/database/models.py`
2. Generate migration: `uv run alembic revision --autogenerate -m "Description"`
3. Review generated migration file
4. Test on development database
5. Apply to production: `uv run alembic upgrade head`

### Backup Before Migrations

```bash
# Backup production database
pg_dump -h hostname -U username -d dbname > backup_$(date +%Y%m%d).sql

# Apply migration
uv run alembic upgrade head

# If issues occur, restore:
psql -h hostname -U username -d dbname < backup_20260204.sql
```

## Troubleshooting

### Common Issues

1. **"Can't locate revision"**
   - Database and migration history are out of sync
   - Fix: `uv run alembic stamp head`

2. **"Target database is not up to date"**
   - Pending migrations need to be applied
   - Fix: `uv run alembic upgrade head`

3. **Connection errors**
   - Check PostgreSQL is running: `pg_isready -h localhost`
   - Verify credentials in `.env`
   - Test connection: `psql -h localhost -U user -d dbname`

4. **Import errors**
   - Ensure dependencies installed: `uv sync --extra api`
   - Check Python path includes `src/`

### Getting Help

- Review [README.md](./README.md) for detailed documentation
- Check [QUICKSTART.md](./QUICKSTART.md) for common workflows
- Run verification script: `uv run python scripts/verify_alembic.py`
- Consult [Alembic docs](https://alembic.sqlalchemy.org/)

## Next Steps

1. **Configure Production Database**
   - Set up PostgreSQL instance
   - Configure environment variables
   - Apply migrations: `uv run alembic upgrade head`

2. **Integrate with FastAPI**
   - Create database session factory
   - Add database dependency to endpoints
   - Implement CRUD operations

3. **Set Up Monitoring**
   - Track migration status
   - Monitor database performance
   - Set up automated backups

4. **Document Custom Migrations**
   - Keep track of schema changes
   - Update this file with new migrations
   - Maintain changelog

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [FastAPI Database Guide](https://fastapi.tiangolo.com/tutorial/sql-databases/)

---

**Installation completed**: 2026-02-04
**Installed by**: Claude Code
**Version**: Initial setup (v001_initial_schema)
