"""Integration tests for PostRepository."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta

from domain.entities.post import Post
from domain.value_objects.embedding import Embedding
from domain.value_objects.url import URL


class TestPostRepository:
    """Integration tests for SqlAlchemyPostRepository."""

    @pytest.mark.asyncio
    async def test_add_and_get_by_id(self, post_repo):
        """Test adding a post and retrieving by ID."""
        embedding = Embedding.from_list([0.1] * 768)
        post = Post(
            id=None,
            title="Test Post",
            summary="Test summary",
            content="Test content",
            clean_url="https://example.com/post/1",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=datetime.now(timezone.utc),
        )

        added = await post_repo.add(post)
        assert added.id is not None
        assert added.title == "Test Post"
        assert added.clean_url == "https://example.com/post/1"

        # Retrieve by ID
        retrieved = await post_repo.get_by_id(added.id)
        assert retrieved is not None
        assert retrieved.id == added.id
        assert retrieved.title == "Test Post"
        assert retrieved.clean_url == "https://example.com/post/1"

    @pytest.mark.asyncio
    async def test_get_by_clean_url(self, post_repo):
        """Test retrieving post by clean URL."""
        embedding = Embedding.from_list([0.1] * 768)
        post = Post(
            id=None,
            title="Test Post",
            summary="Test summary",
            content="Test content",
            clean_url="https://example.com/post/unique",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=datetime.now(timezone.utc),
        )

        added = await post_repo.add(post)

        # Retrieve by clean URL
        retrieved = await post_repo.get_by_clean_url("https://example.com/post/unique")
        assert retrieved is not None
        assert retrieved.id == added.id
        assert retrieved.clean_url == "https://example.com/post/unique"

        # Non-existent URL
        retrieved = await post_repo.get_by_clean_url("https://example.com/nonexistent")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_exists_by_url(self, post_repo):
        """Test checking if post exists by URL."""
        embedding = Embedding.from_list([0.1] * 768)
        post = Post(
            id=None,
            title="Test Post",
            summary="Test summary",
            content="Test content",
            clean_url="https://example.com/post/exists",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=datetime.now(timezone.utc),
        )

        await post_repo.add(post)

        # Should exist
        exists = await post_repo.exists_by_url("https://example.com/post/exists")
        assert exists is True

        # Should not exist
        exists = await post_repo.exists_by_url("https://example.com/post/nonexistent")
        assert exists is False
