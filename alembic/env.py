"""Alembic Environment Configuration.

This script is run by Alembic during migrations.
It configures the database connection and imports models for autogenerate.
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# Add src to path for model imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import models for autogenerate
from infrastructure.db.sqlalchemy_models import Base  # noqa: E402

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
target_metadata = Base.metadata


def get_database_url() -> str:
    """Get database URL from environment or config."""
    # Priority: env var > alembic.ini > default
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    # Fallback to alembic.ini sqlalchemy.url
    url = config.get_main_option("sqlalchemy.url")
    if url:
        return url

    # Default to SQLite for development
    return "sqlite+aiosqlite:///./infostitch.db"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Run migrations with a database connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        # Include schemas for PostgreSQL
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async engine."""
    from sqlalchemy.ext.asyncio import create_async_engine

    # Get database URL and convert to async
    url = get_database_url()

    if url.startswith("sqlite"):
        async_url = url.replace("sqlite://", "sqlite+aiosqlite://")
    else:
        async_url = url.replace("postgresql://", "postgresql+asyncpg://")

    connectable = create_async_engine(
        async_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio

    asyncio.run(run_migrations_online())