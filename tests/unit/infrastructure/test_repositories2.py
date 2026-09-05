"""Unit tests for database repositories - Source, Post, and LLM Model."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select

from domain.entities.llm_model import LLMModel
from domain.entities.post import Post
from domain.entities.rss_source import RssSource
from domain.value_objects.embedding import Embedding
from domain.value_objects.url import URL
from infrastructure.db.repositories.llm_model_repo import SqlAlchemyLLMModelRepository
from infrastructure.db.repositories.post_repo import SqlAlchemyPostRepository
from infrastructure.db.repositories.source_repo import SqlAlchemySourceRepository


class TestSqlAlchemySourceRepository:
    """Tests for SqlAlchemySourceRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession."""
        return AsyncMock()

    @pytest.fixture
    def repo(self, mock_session):
        """Create repository instance."""
        return SqlAlchemySourceRepository(mock_session)

    @pytest.fixture
    def sample_source(self):
        """Create sample RSS source."""
        return RssSource(
            id=1,
            url="https://example.com/rss",
            enabled=True,
        )

    @pytest.mark.asyncio
    async def test_to_entity(self, repo):
        """Test _to_entity conversion."""
        model = MagicMock()
        model.id = 1
        model.url = "https://example.com/rss"
        model.enabled = True
        model.last_fetch = datetime.now(timezone.utc)
        model.created_at = datetime.now(timezone.utc)

        entity = repo._to_entity(model)

        assert entity.id == 1
        assert str(entity.url) == "https://example.com/rss"
        assert entity.enabled is True

    @pytest.mark.asyncio
    async def test_to_model(self, repo, sample_source):
        """Test _to_model conversion."""
        model = repo._to_model(sample_source)

        assert model.id == 1
        assert model.url == "https://example.com/rss"
        assert model.enabled is True

    @pytest.mark.asyncio
    async def test_to_model(self, repo, sample_source):
        """Test _to_model conversion."""
        model = repo._to_model(sample_source)

        assert model.id == 1
        assert model.url == "https://example.com/rss"
        assert model.enabled is True

    @pytest.mark.asyncio
    async def test_add(self, repo, sample_source, mock_session):
        """Test add source."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.url = "https://example.com/rss"
        mock_model.enabled = True
        mock_model.last_fetch = None
        mock_model.created_at = datetime.now(timezone.utc)

        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock(return_value=mock_model)

        with patch("infrastructure.db.repositories.source_repo.RssSourceModel", return_value=mock_model):
            result = await repo.add(sample_source)

        assert result.url == "https://example.com/rss"
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id(self, repo, mock_session):
        """Test get_by_id."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.url = "https://example.com/rss"
        mock_model.enabled = True
        mock_model.last_fetch = None
        mock_model.created_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute.return_value = mock_result

        result = await repo.get_by_id(1)

        assert result is not None
        assert result.id == 1

    @pytest.mark.asyncio
    async def test_get_by_url(self, repo, mock_session):
        """Test get_by_url."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.url = "https://example.com/rss"
        mock_model.enabled = True
        mock_model.last_fetch = None
        mock_model.created_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute.return_value = mock_result

        result = await repo.get_by_url("https://example.com/rss")

        assert result is not None
        assert str(result.url) == "https://example.com/rss"

    @pytest.mark.asyncio
    async def test_get_all(self, repo, mock_session):
        """Test get_all."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.url = "https://example.com/rss"
        mock_model.enabled = True
        mock_model.last_fetch = None
        mock_model.created_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        result = await repo.get_all()

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_all_enabled_only(self, repo, mock_session):
        """Test get_all with enabled_only=True."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.url = "https://example.com/rss"
        mock_model.enabled = True
        mock_model.last_fetch = None
        mock_model.created_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        result = await repo.get_all(enabled_only=True)

        assert len(result) == 1
        assert result[0].enabled is True

    @pytest.mark.asyncio
    async def test_get_enabled(self, repo, mock_session):
        """Test get_enabled delegates to get_all."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.url = "https://example.com/rss"
        mock_model.enabled = True
        mock_model.last_fetch = None
        mock_model.created_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        result = await repo.get_enabled()

        assert len(result) == 1
        assert result[0].enabled is True

    @pytest.mark.asyncio
    async def test_update(self, repo, sample_source, mock_session):
        """Test update source."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.url = "https://old.com/rss"
        mock_model.enabled = True
        mock_model.last_fetch = None
        mock_model.created_at = datetime.now(timezone.utc)

        mock_session.get.return_value = mock_model
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        sample_source.url = "https://new.com/rss"
        result = await repo.update(sample_source)

        assert str(result.url) == "https://new.com/rss"
        assert mock_model.url == "https://new.com/rss"
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_not_found(self, repo, sample_source, mock_session):
        """Test update when source not found."""
        mock_session.get.return_value = None

        with pytest.raises(ValueError, match="Source 1 not found"):
            await repo.update(sample_source)

    @pytest.mark.asyncio
    async def test_delete(self, repo, mock_session):
        """Test delete source."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repo.delete(1)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repo, mock_session):
        """Test delete when source not found."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        result = await repo.delete(999)
        assert result is False

    @pytest.mark.asyncio
    async def test_update_last_fetch(self, repo, mock_session):
        """Test update_last_fetch."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repo.update_last_fetch(1)

        assert result is True

    @pytest.mark.asyncio
    async def test_count(self, repo, mock_session):
        """Test count sources."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 10
        mock_session.execute.return_value = mock_result

        result = await repo.count()

        assert result == 10



class TestSqlAlchemyPostRepository:
    """Tests for SqlAlchemyPostRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession."""
        return AsyncMock()

    @pytest.fixture
    def repo(self, mock_session):
        """Create repository instance."""
        return SqlAlchemyPostRepository(mock_session)

    @pytest.fixture
    def sample_post(self):
        """Create sample post."""
        return Post(
            id=1,
            article_id=1,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            title="Test Post",
            summary="Test summary",
            content="Test content",
            clean_url=URL.from_string("https://example.com/post"),
            embedding=Embedding([0.1] * 768),
            image_url="https://example.com/image.jpg",
            is_duplicate=False,
        )

    @pytest.mark.asyncio
    async def test_to_entity(self, repo):
        """Test _to_entity conversion."""
        model = MagicMock()
        model.id = 1
        model.clean_url = "https://example.com/post"
        model.title = "Test Post"
        model.summary = "Test summary"
        model.embedding = [0.1] * 768
        model.is_duplicate = False
        model.source_id = 1
        model.channel_id = 1
        model.llm_model_id = 1
        model.template_id = "news_brief"
        model.post_text = "Test content"
        model.image_url = "https://example.com/image.jpg"
        model.created_at = datetime.now(timezone.utc)

        entity = repo._to_entity(model)

        assert entity.id == 1
        assert entity.title == "Test Post"
        assert entity.summary == "Test summary"
        assert entity.content == "Test content"
        assert str(entity.clean_url) == "https://example.com/post"
        assert entity.embedding is not None
        assert len(entity.embedding.vector) == 768
        assert entity.is_duplicate is False

    @pytest.mark.asyncio
    async def test_to_model(self, repo, sample_post):
        """Test _to_model conversion."""
        model = repo._to_model(sample_post)

        assert model.id == 1
        assert str(model.clean_url) == "https://example.com/post"
        assert model.title == "Test Post"
        assert model.summary == "Test summary"
        assert model.post_text == "Test content"
        assert model.image_url == "https://example.com/image.jpg"
        assert model.is_duplicate is False
        assert model.source_id == 1
        assert model.channel_id == 1
        assert model.llm_model_id == 1
        assert model.template_id == "news_brief"



class TestSqlAlchemyPostRepository:
    """Tests for SqlAlchemyPostRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession."""
        return AsyncMock()

    @pytest.fixture
    def repo(self, mock_session):
        """Create repository instance."""
        return SqlAlchemyPostRepository(mock_session)

    @pytest.fixture
    def sample_post(self):
        """Create sample post."""
        return Post(
            id=1,
            article_id=1,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            title="Test Post",
            summary="Test summary",
            content="Test content",
            clean_url=URL.from_string("https://example.com/post"),
            embedding=Embedding([0.1] * 768),
            image_url="https://example.com/image.jpg",
            is_duplicate=False,
        )

    @pytest.mark.asyncio
    async def test_to_entity(self, repo):
        """Test _to_entity conversion."""
        model = MagicMock()
        model.id = 1
        model.clean_url = "https://example.com/post"
        model.title = "Test Post"
        model.summary = "Test summary"
        model.embedding = [0.1] * 768
        model.is_duplicate = False
        model.source_id = 1
        model.channel_id = 1
        model.llm_model_id = 1
        model.template_id = "news_brief"
        model.post_text = "Test content"
        model.image_url = "https://example.com/image.jpg"
        model.created_at = datetime.now(timezone.utc)

        entity = repo._to_entity(model)

        assert entity.id == 1
        assert entity.title == "Test Post"
        assert entity.summary == "Test summary"
        assert entity.content == "Test content"
        assert str(entity.clean_url) == "https://example.com/post"
        assert entity.embedding is not None
        assert len(entity.embedding.vector) == 768
        assert entity.is_duplicate is False

    @pytest.mark.asyncio
    async def test_to_model(self, repo, sample_post):
        """Test _to_model conversion."""
        model = repo._to_model(sample_post)

        assert model.id == 1
        assert str(model.clean_url) == "https://example.com/post"
        assert model.title == "Test Post"
        assert model.summary == "Test summary"
        assert model.post_text == "Test content"
        assert model.image_url == "https://example.com/image.jpg"
        assert model.is_duplicate is False
        assert model.source_id == 1
        assert model.channel_id == 1
        assert model.llm_model_id == 1
        assert model.template_id == "news_brief"

class TestSqlAlchemyLLMModelRepository:
    """Tests for SqlAlchemyLLMModelRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession."""
        return AsyncMock()

    @pytest.fixture
    def repo(self, mock_session):
        """Create repository instance."""
        return SqlAlchemyLLMModelRepository(mock_session)

    @pytest.fixture
    def sample_model(self):
        """Create sample LLM model."""
        return LLMModel(
            id=1,
            name="gpt-4",
            provider="openai",
            model_id="gpt-4",
            api_key_ref="OPENAI_API_KEY",
            is_active=True,
        )

    @pytest.mark.asyncio
    async def test_to_entity(self, repo):
        """Test _to_entity conversion."""
        model = MagicMock()
        model.id = 1
        model.name = "gpt-4"
        model.provider = "openai"
        model.model_id = "gpt-4"
        model.api_key_ref = "OPENAI_API_KEY"
        model.is_active = True
        model.created_at = datetime.now(timezone.utc)

        entity = repo._to_entity(model)

        assert entity.id == 1
        assert entity.name == "gpt-4"
        assert entity.provider == "openai"
        assert entity.model_id == "gpt-4"
        assert entity.api_key_ref == "OPENAI_API_KEY"
        assert entity.is_active is True

    @pytest.mark.asyncio
    async def test_to_model(self, repo, sample_model):
        """Test _to_model conversion."""
        model = repo._to_model(sample_model)

        assert model.id == 1
        assert model.name == "gpt-4"
        assert model.provider == "openai"
        assert model.model_id == "gpt-4"
        assert model.api_key_ref == "OPENAI_API_KEY"
        assert model.is_active is True

    @pytest.mark.asyncio
    async def test_add(self, repo, sample_model, mock_session):
        """Test add LLM model."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.name = "gpt-4"
        mock_model.provider = "openai"
        mock_model.model_id = "gpt-4"
        mock_model.api_key_ref = "OPENAI_API_KEY"
        mock_model.is_active = True
        mock_model.created_at = datetime.now(timezone.utc)

        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock(return_value=mock_model)

        with patch("infrastructure.db.repositories.llm_model_repo.LLMModelModel", return_value=mock_model):
            result = await repo.add(sample_model)

        assert result.name == "gpt-4"
        assert result.provider == "openai"
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id(self, repo, mock_session):
        """Test get_by_id."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.name = "gpt-4"
        mock_model.provider = "openai"
        mock_model.model_id = "gpt-4"
        mock_model.api_key_ref = "OPENAI_API_KEY"
        mock_model.is_active = True
        mock_model.created_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute.return_value = mock_result

        result = await repo.get_by_id(1)

        assert result is not None
        assert result.name == "gpt-4"
        assert result.provider == "openai"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repo, mock_session):
        """Test get_by_id when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repo.get_by_id(999)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_name(self, repo, mock_session):
        """Test get_by_name."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.name = "gpt-4"
        mock_model.provider = "openai"
        mock_model.model_id = "gpt-4"
        mock_model.api_key_ref = "OPENAI_API_KEY"
        mock_model.is_active = True
        mock_model.created_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute.return_value = mock_result

        result = await repo.get_by_name("gpt-4")

        assert result is not None
        assert result.name == "gpt-4"

    @pytest.mark.asyncio
    async def test_get_all(self, repo, mock_session):
        """Test get_all."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.name = "gpt-4"
        mock_model.provider = "openai"
        mock_model.model_id = "gpt-4"
        mock_model.api_key_ref = "OPENAI_API_KEY"
        mock_model.is_active = True
        mock_model.created_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        result = await repo.get_all()

        assert len(result) == 1
        assert result[0].name == "gpt-4"

    @pytest.mark.asyncio
    async def test_get_all_active_only(self, repo, mock_session):
        """Test get_all with active_only=True."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.name = "gpt-4"
        mock_model.provider = "openai"
        mock_model.model_id = "gpt-4"
        mock_model.api_key_ref = "OPENAI_API_KEY"
        mock_model.is_active = True
        mock_model.created_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        result = await repo.get_all(active_only=True)

        assert len(result) == 1
        assert result[0].is_active is True

    @pytest.mark.asyncio
    async def test_get_active(self, repo, mock_session):
        """Test get_active delegates to get_all."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.name = "gpt-4"
        mock_model.provider = "openai"
        mock_model.model_id = "gpt-4"
        mock_model.api_key_ref = "OPENAI_API_KEY"
        mock_model.is_active = True
        mock_model.created_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        result = await repo.get_active()

        assert len(result) == 1
        assert result[0].is_active is True

    @pytest.mark.asyncio
    async def test_get_by_provider(self, repo, mock_session):
        """Test get_by_provider."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.name = "gpt-4"
        mock_model.provider = "openai"
        mock_model.model_id = "gpt-4"
        mock_model.api_key_ref = "OPENAI_API_KEY"
        mock_model.is_active = True
        mock_model.created_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        result = await repo.get_by_provider("openai")

        assert len(result) == 1
        assert result[0].provider == "openai"

    @pytest.mark.asyncio
    async def test_update(self, repo, sample_model, mock_session):
        """Test update LLM model."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.name = "old-name"
        mock_model.provider = "openai"
        mock_model.model_id = "gpt-3.5"
        mock_model.api_key_ref = "OLD_KEY"
        mock_model.is_active = False
        mock_model.created_at = datetime.now(timezone.utc)

        mock_session.get.return_value = mock_model
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        sample_model.name = "updated-name"
        sample_model.is_active = True
        result = await repo.update(sample_model)

        assert result.name == "updated-name"
        assert result.is_active is True
        assert mock_model.name == "updated-name"
        assert mock_model.is_active is True
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_not_found(self, repo, sample_model, mock_session):
        """Test update when model not found."""
        mock_session.get.return_value = None

        with pytest.raises(ValueError, match="LLM Model 1 not found"):
            await repo.update(sample_model)

    @pytest.mark.asyncio
    async def test_delete(self, repo, mock_session):
        """Test delete LLM model."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repo.delete(1)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repo, mock_session):
        """Test delete when model not found."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        result = await repo.delete(999)
        assert result is False

    @pytest.mark.asyncio
    async def test_count(self, repo, mock_session):
        """Test count LLM models."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 3
        mock_session.execute.return_value = mock_result

        result = await repo.count()

        assert result == 3

