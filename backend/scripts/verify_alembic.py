#!/usr/bin/env python3
"""
Verify Alembic setup and database connectivity.

This script checks:
1. Environment variables are configured
2. Database connection is working
3. Alembic configuration is valid
4. Migration files are accessible

Usage:
    cd backend
    uv run python scripts/verify_alembic.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_environment():
    """Check if required environment variables are set."""
    print("=" * 70)
    print("STEP 1: Checking Environment Variables")
    print("=" * 70)

    from src.config.settings import settings

    checks = {
        "POSTGRES_HOST": settings.postgres_host,
        "POSTGRES_PORT": settings.postgres_port,
        "POSTGRES_DB": settings.postgres_db,
        "POSTGRES_USER": settings.postgres_user,
        "POSTGRES_PASSWORD": settings.postgres_password,
        "DATABASE_URL": settings.database_url,
    }

    all_good = True
    for key, value in checks.items():
        status = "✓" if value else "✗"
        # Mask password
        display_value = "***" if "PASSWORD" in key and value else value
        print(f"  {status} {key}: {display_value}")
        if not value and key != "POSTGRES_PASSWORD":
            all_good = False

    if not all_good:
        print("\n⚠️  Warning: Some environment variables are not set!")
        print("   Check your .env file in the backend or project root directory.")
        return False

    print("\n✓ Environment variables configured correctly!")
    return True


def check_database_connection():
    """Test database connectivity."""
    print("\n" + "=" * 70)
    print("STEP 2: Testing Database Connection")
    print("=" * 70)

    try:
        import asyncio

        import asyncpg
        from src.config.settings import settings

        async def test_connection():
            try:
                conn = await asyncpg.connect(
                    host=settings.postgres_host,
                    port=settings.postgres_port,
                    user=settings.postgres_user,
                    password=settings.postgres_password,
                    database=settings.postgres_db,
                    timeout=5,
                )
                version = await conn.fetchval("SELECT version()")
                await conn.close()
                return version
            except Exception as e:
                return str(e)

        version = asyncio.run(test_connection())

        if "PostgreSQL" in version:
            print(f"  ✓ Database connection successful!")
            print(f"  ✓ PostgreSQL version: {version.split(',')[0]}")
            return True
        else:
            print(f"  ✗ Database connection failed: {version}")
            return False

    except ImportError:
        print("  ✗ asyncpg not installed. Run: uv sync --extra api")
        return False
    except Exception as e:
        print(f"  ✗ Connection test failed: {e}")
        return False


def check_alembic_config():
    """Verify Alembic configuration files exist."""
    print("\n" + "=" * 70)
    print("STEP 3: Checking Alembic Configuration")
    print("=" * 70)

    backend_dir = Path(__file__).parent.parent
    files_to_check = [
        backend_dir / "alembic.ini",
        backend_dir / "alembic" / "env.py",
        backend_dir / "alembic" / "script.py.mako",
        backend_dir / "alembic" / "versions" / "001_initial_schema.py",
        backend_dir / "alembic" / "README.md",
    ]

    all_exist = True
    for file_path in files_to_check:
        if file_path.exists():
            print(f"  ✓ {file_path.name}")
        else:
            print(f"  ✗ {file_path.name} NOT FOUND")
            all_exist = False

    if not all_exist:
        print("\n⚠️  Warning: Some Alembic files are missing!")
        return False

    print("\n✓ Alembic configuration files present!")
    return True


def check_models():
    """Check if database models can be imported."""
    print("\n" + "=" * 70)
    print("STEP 4: Checking Database Models")
    print("=" * 70)

    try:
        from src.database.models import Base, MessageModel, SessionModel

        print(f"  ✓ Base model imported")
        print(f"  ✓ SessionModel imported")
        print(f"  ✓ MessageModel imported")

        # Check metadata
        tables = list(Base.metadata.tables.keys())
        print(f"\n  Tables in metadata: {', '.join(tables)}")

        if "sessions" in tables and "messages" in tables:
            print("\n✓ Database models configured correctly!")
            return True
        else:
            print("\n✗ Expected tables not found in metadata!")
            return False

    except ImportError as e:
        print(f"  ✗ Failed to import models: {e}")
        return False


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("""
To run Alembic migrations:

1. View current database version:
   uv run alembic current

2. Apply migrations to database:
   uv run alembic upgrade head

3. View migration history:
   uv run alembic history

4. Create new migration after model changes:
   uv run alembic revision --autogenerate -m "Description"

5. Rollback last migration:
   uv run alembic downgrade -1

For more information, see:
- backend/alembic/README.md
- backend/alembic/QUICKSTART.md
""")


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("ALEMBIC SETUP VERIFICATION")
    print("=" * 70)

    results = {
        "Environment": check_environment(),
        "Database": check_database_connection(),
        "Alembic Config": check_alembic_config(),
        "Models": check_models(),
    }

    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    all_passed = True
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {check}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n" + "=" * 70)
        print("🎉 ALL CHECKS PASSED!")
        print("=" * 70)
        print("\nYour Alembic setup is ready to use!")
        print_next_steps()
        return 0
    else:
        print("\n" + "=" * 70)
        print("⚠️  SOME CHECKS FAILED")
        print("=" * 70)
        print("\nPlease fix the issues above before using Alembic.")
        print("\nCommon solutions:")
        print("  • Ensure PostgreSQL is running")
        print("  • Check .env file has correct database credentials")
        print("  • Run: uv sync --extra api")
        return 1


if __name__ == "__main__":
    sys.exit(main())
