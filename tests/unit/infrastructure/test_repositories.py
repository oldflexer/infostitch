"""Unit tests for database repositories."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select

from domain.entities.article import Article
from domain.entities.channel import Channel
from domain.entities.post import Post
from domain.entities.rss_source import RssSource
from domain.value_objects.embedding import Embedding
from domain.value_objects.url import URL
from infrastructure.db.repositories.article_repo import SqlAlchemyArticleRepository
from infrastructure.db.repositories.channel_repo import SqlAlchemyChannelRepository
from infrastructure.db.repositories.post_repo import SqlAlchemyPostRepository
from infrastructure.db.repositories.source_repo import SqlAlchemySourceRepository


class TestSqlAlchemyArticleRepository:
    """Tests for SqlAlchemyArticleRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession."""
        return AsyncMock()

    @pytest.fixture
    def repo(self, mock_session):
        """Create repository instance."""
        return SqlAlchemyArticleRepository(mock_session)

    @pytest.fixture
    def sample_article(self):
        """Create sample article."""
        return Article(
            id=1,
            title="Test Article",
            url=URL.from_string("https://example.com/article"),
            content="Test content",
            source_id=1,
        )

    @pytest.mark.asyncio
    async def test_add(self, repo, sample_article):
        """Test adding article returns same article."""
        result = await repo.add(sample_article)
        assert result == sample_article

    @pytest.mark.asyncio
    async def test_get_by_id(self, repo):
        """Test get_by_id returns None."""
        result = await repo.get_by_id(1)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_url(self, repo):
        """Test get_by_url returns None."""
        result = await repo.get_by_url("https://example.com/article")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_source(self, repo):
        """Test get_by_source returns empty list."""
        result = await repo.get_by_source(1)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_recent(self, repo):
        """Test get_recent returns empty list."""
        result = await repo.get_recent()
        assert result == []

    @pytest.mark.asyncio
    async def test_get_unprocessed(self, repo):
        """Test get_unprocessed returns empty list."""
        result = await repo.get_unprocessed()
        assert result == []

    @pytest.mark.asyncio
    async def test_update(self, repo, sample_article):
        """Test update returns same article."""
        result = await repo.update(sample_article)
        assert result == sample_article

    @pytest.mark.asyncio
    async def test_delete(self, repo):
        """Test delete returns False."""
        result = await repo.delete(1)
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_by_url(self, repo):
        """Test exists_by_url returns False."""
        result = await repo.exists_by_url("https://example.com/article")
        assert result is False

    @pytest.mark.asyncio
    async def test_count_by_source(self, repo):
        """Test count_by_source returns 0."""
        result = await repo.count_by_source(1)
        assert result == 0



class TestSqlAlchemyChannelRepository:
    """Tests for SqlAlchemyChannelRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession."""
        return AsyncMock()

    @pytest.fixture
    def repo(self, mock_session):
        """Create repository instance."""
        return SqlAlchemyChannelRepository(mock_session)

    @pytest.fixture
    def sample_channel(self):
        """Create sample channel."""
        return Channel(
            id=1,
            name="Test Channel",
            type="telegram",
            enabled=True,
            config={"chat_id": "12345", "bot_token_ref": "TELEGRAM_BOT_TOKEN"},
        )

    @pytest.mark.asyncio
    async def test_to_entity(self, repo):
        """Test _to_entity conversion."""
        model = MagicMock()
        model.id = 1
        model.name = "Test Channel"
        model.type = "telegram"
        model.enabled = True
        model.config_json = {"chat_id": "12345", "bot_token_ref": "TELEGRAM_BOT_TOKEN"}
        model.created_at = datetime.now(timezone.utc)

        entity = repo._to_entity(model)

        assert entity.id == 1
        assert entity.name == "Test Channel"
        assert entity.type == "telegram"
        assert entity.enabled is True
        assert entity.config == {"chat_id": "12345", "bot_token_ref": "TELEGRAM_BOT_TOKEN"}

    @pytest.mark.asyncio
    async def test_to_model(self, repo, sample_channel):
        """Test _to_model conversion."""
        model = repo._to_model(sample_channel)

        assert model.id == 1
        assert model.name == "Test Channel"
        assert model.type == "telegram"
        assert model.enabled is True
        assert model.config_json == {"chat_id": "12345", "bot_token_ref": "TELEGRAM_BOT_TOKEN"}

    @pytest.mark.asyncio
    async def test_add(self, repo, sample_channel, mock_session):
        """Test add channel."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.name = "Test Channel"
        mock_model.type = "telegram"
        mock_model.enabled = True
        mock_model.config_json = {"chat_id": "12345", "bot_token_ref": "TELEGRAM_BOT_TOKEN"}
        mock_model.created_at = datetime.now(timezone.utc)

        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock(return_value=mock_model)

        with patch("infrastructure.db.repositories.channel_repo.ChannelModel", return_value=mock_model):
            result = await repo.add(sample_channel)

        assert result.name == "Test Channel"
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id(self, repo, mock_session):
        """Test get_by_id."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.name = "Test Channel"
        mock_model.type = "telegram"
        mock_model.enabled = True
        mock_model.config_json = {"chat_id": "12345", "bot_token_ref": "TELEGRAM_BOT_TOKEN"}
        mock_model.created_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute.return_value = mock_result

        result = await repo.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.name == "Test Channel"

