"""Unit tests for SQLAlchemy models."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import inspect

from infrastructure.db.sqlalchemy_models import (
    Base,
    Channel,
    LLMModel,
    Log,
    PublishedPost,
    RssSource,
    Setting,
    User,
    utc_now,
)
from infrastructure.db.session import DatabaseManager


class TestUtcNow:
    """Tests for utc_now function."""

    def test_utc_now_returns_datetime(self):
        """Test utc_now returns datetime with UTC timezone."""
        result = utc_now()
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc


class TestBaseModel:
    """Tests for Base model configuration."""

    def test_base_type_annotation_map(self):
        """Test Base has correct type annotation map."""
        assert hasattr(Base, "type_annotation_map")
        assert Dict[str, Any] in Base.type_annotation_map
        assert List[float] in Base.type_annotation_map


class TestRssSource:
    """Tests for RssSource model."""

    def test_rss_source_tablename(self):
        """Test RssSource table name."""
        assert RssSource.__tablename__ == "rss_sources"

    def test_rss_source_columns(self):
        """Test RssSource has expected columns."""
        mapper = inspect(RssSource)
        columns = {c.key for c in mapper.columns}
        expected = {"id", "url", "enabled", "last_fetch", "created_at"}
        assert expected.issubset(columns)

    def test_rss_source_repr(self):
        """Test RssSource __repr__."""
        source = RssSource(id=1, url="https://example.com/rss", enabled=True)
        repr_str = repr(source)
        assert "RssSource" in repr_str
        assert "1" in repr_str
        assert "https://example.com/rss" in repr_str


class TestChannel:
    """Tests for Channel model."""

    def test_channel_tablename(self):
        """Test Channel table name."""
        assert Channel.__tablename__ == "channels"

    def test_channel_columns(self):
        """Test Channel has expected columns."""
        mapper = inspect(Channel)
        columns = {c.key for c in mapper.columns}
        expected = {"id", "name", "type", "enabled", "config_json", "created_at"}
        assert expected.issubset(columns)

    def test_channel_repr(self):
        """Test Channel __repr__."""
        channel = Channel(id=1, name="Test Channel", type="telegram", enabled=True, config_json={})
        repr_str = repr(channel)
        assert "Channel" in repr_str
        assert "1" in repr_str
        assert "Test Channel" in repr_str
        assert "telegram" in repr_str


class TestSetting:
    """Tests for Setting model."""

    def test_setting_tablename(self):
        """Test Setting table name."""
        assert Setting.__tablename__ == "settings"

    def test_setting_columns(self):
        """Test Setting has expected columns."""
        mapper = inspect(Setting)
        columns = {c.key for c in mapper.columns}
        expected = {"key", "value", "description"}
        assert expected.issubset(columns)


class TestLLMModel:
    """Tests for LLMModel model."""

    def test_llm_model_tablename(self):
        """Test LLMModel table name."""
        assert LLMModel.__tablename__ == "llm_models"

    def test_llm_model_columns(self):
        """Test LLMModel has expected columns."""
        mapper = inspect(LLMModel)
        columns = {c.key for c in mapper.columns}
        expected = {"id", "name", "provider", "model_id", "api_key_ref", "is_active", "created_at"}
        assert expected.issubset(columns)

    def test_llm_model_repr(self):
        """Test LLMModel __repr__."""
        model = LLMModel(id=1, name="gpt-4", provider="openai", model_id="gpt-4", api_key_ref="KEY", is_active=True)
        repr_str = repr(model)
        assert "LLMModel" in repr_str
        assert "1" in repr_str
        assert "gpt-4" in repr_str
        assert "openai" in repr_str


class TestUser:
    """Tests for User model."""

    def test_user_tablename(self):
        """Test User table name."""
        assert User.__tablename__ == "users"

    def test_user_columns(self):
        """Test User has expected columns."""
        mapper = inspect(User)
        columns = {c.key for c in mapper.columns}
        expected = {"id", "username", "password_hash", "role", "created_at", "last_login"}
        assert expected.issubset(columns)


class TestPublishedPost:
    """Tests for PublishedPost model."""

    def test_published_post_tablename(self):
        """Test PublishedPost table name."""
        assert PublishedPost.__tablename__ == "published_posts"

    def test_published_post_columns(self):
        """Test PublishedPost has expected columns."""
        mapper = inspect(PublishedPost)
        columns = {c.key for c in mapper.columns}
        expected = {"id", "source_id", "channel_id", "llm_model_id", "template_id",
                    "title", "summary", "post_text", "clean_url", "embedding", "image_url",
                    "is_duplicate", "created_at"}
        assert expected.issubset(columns)


class TestLog:
    """Tests for Log model."""

    def test_log_tablename(self):
        """Test Log table name."""
        assert Log.__tablename__ == "logs"

    def test_log_columns(self):
        """Test Log has expected columns."""
        mapper = inspect(Log)
        columns = {c.key for c in mapper.columns}
        expected = {"id", "timestamp", "level", "module", "message", "context_json", "user_id"}
        assert expected.issubset(columns)

    def test_log_repr(self):
        """Test Log __repr__."""
        log = Log(id=1, level="INFO", module="test.module", message="Test message")
        repr_str = repr(log)
        assert "Log" in repr_str
        assert "1" in repr_str
        assert "INFO" in repr_str
        assert "test.module" in repr_str


class TestDatabaseManager:
    """Tests for DatabaseManager."""

    def test_database_manager_initialization(self):
        """Test DatabaseManager initialization with default URL."""
        manager = DatabaseManager("sqlite:///test.db")
        assert manager._database_url == "sqlite:///test.db"
        assert manager._engine is None
        assert manager._session_factory is None

    def test_database_manager_engine_property(self):
        """Test engine property creates engine on first access."""
        manager = DatabaseManager("sqlite:///test.db")
        engine = manager.engine
        assert engine is not None
        assert manager._engine is engine

    def test_database_manager_session_factory_property(self):
        """Test session_factory property creates factory on first access."""
        manager = DatabaseManager("sqlite:///test.db")
        factory = manager.session_factory
        assert factory is not None
        assert manager._session_factory is factory

    def test_database_manager_create_engine_sqlite(self):
        """Test _create_engine with SQLite URL."""
        manager = DatabaseManager("sqlite:///test.db")
        engine = manager._create_engine()
        assert engine is not None
        # Verify it's an async engine
        from sqlalchemy.ext.asyncio import AsyncEngine
        assert isinstance(engine, AsyncEngine)

    def test_database_manager_create_engine_postgresql(self):
        """Test _create_engine with PostgreSQL URL."""
        manager = DatabaseManager("postgresql://user:pass@localhost/db")
        engine = manager._create_engine()
        assert engine is not None
        from sqlalchemy.ext.asyncio import AsyncEngine
        assert isinstance(engine, AsyncEngine)