"""SQLAlchemy ORM Models for InfoStitch.

Maps to the database schema defined in docs/DB.md.
Supports both SQLite (dev) and PostgreSQL + pgvector (prod).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, VECTOR
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    # SQLite doesn't support JSONB, use JSON instead
    # PostgreSQL will use JSONB via dialect-specific type
    type_annotation_map = {
        Dict[str, Any]: JSONB().with_variant(JSONB, "postgresql"),
        List[float]: VECTOR(768).with_variant(VECTOR(768), "postgresql"),
    }


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class RssSource(Base):
    """RSS feed configuration."""

    __tablename__ = "rss_sources"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_fetch: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    published_posts: Mapped[List["PublishedPost"]] = relationship(
        back_populates="source", lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<RssSource(id={self.id}, url={self.url}, enabled={self.enabled})>"


class Channel(Base):
    """Publishing destination (Telegram, VK, Max)."""

    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # telegram, vk, max
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    config_json: Mapped[Dict[str, Any]] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    published_posts: Mapped[List["PublishedPost"]] = relationship(
        back_populates="channel", lazy="dynamic"
    )

    def __repr__(self) -> str:
class Setting(Base):
    """Dynamic configuration key-value store."""

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Setting(key={self.key}, value={self.value[:50]}...)>"


class PublishedPost(Base):
    """Published article with embedding for deduplication."""

    __tablename__ = "published_posts"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    clean_url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[List[float]] = mapped_column(
        VECTOR(768).with_variant(VECTOR(768), "postgresql"),
        nullable=False,
    )
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("rss_sources.id", ondelete="SET NULL"), nullable=True
    )
    channel_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("channels.id", ondelete="SET NULL"), nullable=True
    )
    llm_model_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("llm_models.id", ondelete="SET NULL"), nullable=True
    )
    template_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    post_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    source: Mapped[Optional["RssSource"]] = relationship(back_populates="published_posts")
    channel: Mapped[Optional["Channel"]] = relationship(back_populates="published_posts")
    llm_model: Mapped[Optional["LLMModel"]] = relationship(back_populates="published_posts")

    # Table-level constraints and indexes
    __table_args__ = (
        UniqueConstraint("clean_url", name="uq_published_posts_clean_url"),
        Index("ix_published_posts_created_at", "created_at"),
        Index(
            "ix_published_posts_is_duplicate",
            "is_duplicate",
            postgresql_where=Text("is_duplicate = false"),
        ),
    )

    def __repr__(self) -> str:
        return f"<PublishedPost(id={self.id}, title={self.title[:50]}, duplicate={self.is_duplicate})>"


class User(Base):
    """Dashboard user account."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="admin", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    logs: Mapped[List["Log"]] = relationship(back_populates="user", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


class Log(Base):
    """Structured application log entry."""

    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
# =============================================================================
# Database Engine & Session Helpers
# =============================================================================

from sqlalchemy import create_engine, Text
from sqlalchemy.pool import NullPool


def create_engine_from_url(database_url: str):
    """Create SQLAlchemy engine from database URL.

    Handles both SQLite and PostgreSQL with appropriate connect args.
    """
    if database_url.startswith("sqlite"):
        # SQLite specific: enable WAL mode for better concurrency
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        # Enable WAL mode
        with engine.connect() as conn:
            conn.execute(Text("PRAGMA journal_mode=WAL;"))
    else:
        # PostgreSQL
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    return engine


def create_async_engine_from_url(database_url: str):
    """Create async SQLAlchemy engine from database URL."""
    from sqlalchemy.ext.asyncio import create_async_engine

    if database_url.startswith("sqlite"):
        # Convert to async SQLite URL
        async_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")
        engine = create_async_engine(
            async_url,
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
    else:
        # Convert to async PostgreSQL URL
        async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        engine = create_async_engine(
            async_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    return engine
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    level: Mapped[str] = mapped_column(String(10), nullable=False)
    module: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    context_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(back_populates="logs")

    # Indexes
    __table_args__ = (
        Index("ix_logs_timestamp", "timestamp"),
        Index("ix_logs_level", "level"),
        Index("ix_logs_module", "module"),
    )

    def __repr__(self) -> str:
        return f"<Log(id={self.id}, level={self.level}, module={self.module})>"
        return f"<Channel(id={self.id}, name={self.name}, type={self.type})>"


class LLMModel(Base):
    """LLM provider configuration."""

    __tablename__ = "llm_models"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    api_key_ref: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    published_posts: Mapped[List["PublishedPost"]] = relationship(
        back_populates="llm_model", lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<LLMModel(id={self.id}, name={self.name}, provider={self.provider})>"