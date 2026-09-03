"""Database Session Management.

Provides async session factory and dependency injection for database sessions.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from infrastructure.config import get_settings


class DatabaseManager:
    """Manages database engine and session lifecycle."""

    def __init__(self, database_url: Optional[str] = None):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._database_url = database_url or get_settings().database_url

    @property
    def engine(self) -> AsyncEngine:
        """Get or create async engine."""
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get or create session factory."""
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )
        return self._session_factory

    def _create_engine(self) -> AsyncEngine:
        """Create async engine with appropriate configuration."""
        url = self._database_url

        if url.startswith("sqlite"):
            # Handle both sqlite:// and sqlite+aiosqlite://
            if url.startswith("sqlite://"):
                async_url = url.replace("sqlite://", "sqlite+aiosqlite://")
            else:
                async_url = url
            engine = create_async_engine(
                async_url,
                connect_args={"check_same_thread": False},
                poolclass=NullPool,
                echo=False,
            )
        else:
            # Handle both postgresql:// and postgresql+asyncpg://
            if url.startswith("postgresql://"):
                async_url = url.replace(
                    "postgresql://", "postgresql+asyncpg://")
            else:
                async_url = url
            engine = create_async_engine(
                async_url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                echo=False,
            )
        return engine

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide a transactional scope as a context manager."""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close(self) -> None:
        """Close the engine and cleanup."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session."""
    db_manager = get_db_manager()
    async with db_manager.session() as session:
        yield session


async def init_db() -> None:
    """Initialize database (create tables if not exist)."""
    from infrastructure.db.sqlalchemy_models import Base

    db_manager = get_db_manager()
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    db_manager = get_db_manager()
    await db_manager.close()
