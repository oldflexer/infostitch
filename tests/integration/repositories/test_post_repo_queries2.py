"""Integration tests for PostRepository - More query methods."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta

from domain.entities.post import Post
from domain.value_objects.embedding import Embedding


class TestPostRepositoryQueries2:
    """More integration tests for SqlAlchemyPostRepository query methods."""

    @pytest.mark.asyncio
    async def test_get_by_source(self, post_repo):
        """Test getting posts by source ID."""
        embedding = Embedding.from_list([0.1] * 768)
        now = datetime.now(timezone.utc)

        # Add posts from different sources
        post1 = Post(
            id=None,
            title="Source 1 Post",
            summary="Summary",
            content="Content",
            clean_url="https://example.com/source1",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        post2 = Post(
            id=None,
            title="Source 2 Post",
            summary="Summary",
            content="Content",
            clean_url="https://example.com/source2",
            embedding=embedding,
            is_duplicate=False,
            source_id=2,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        await post_repo.add(post1)
        await post_repo.add(post2)

        # Get by source 1
        posts = await post_repo.get_by_source(source_id=1, limit=100)
        assert len(posts) == 1
        assert posts[0].source_id == 1

        # Get by source 2
        posts = await post_repo.get_by_source(source_id=2, limit=100)
        assert len(posts) == 1
        assert posts[0].source_id == 2

    @pytest.mark.asyncio
    async def test_get_by_channel(self, post_repo):
        """Test getting posts by channel ID."""
        embedding = Embedding.from_list([0.1] * 768)
        now = datetime.now(timezone.utc)

        # Add posts from different channels
        post1 = Post(
            id=None,
            title="Channel 1 Post",
            summary="Summary",
            content="Content",
            clean_url="https://example.com/channel1",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        post2 = Post(
            id=None,
            title="Channel 2 Post",
            summary="Summary",
            content="Content",
            clean_url="https://example.com/channel2",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=2,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        await post_repo.add(post1)
        await post_repo.add(post2)

        # Get by channel 1
        posts = await post_repo.get_by_channel(channel_id=1, limit=100)
        assert len(posts) == 1
        assert posts[0].channel_id == 1

    @pytest.mark.asyncio
    async def test_get_duplicates(self, post_repo):
        """Test getting duplicate posts."""
        embedding = Embedding.from_list([0.1] * 768)
        now = datetime.now(timezone.utc)

        # Add unique post
        post1 = Post(
            id=None,
            title="Unique Post",
            summary="Summary",
            content="Content",
            clean_url="https://example.com/unique",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        # Add duplicate post
        post2 = Post(
            id=None,
            title="Duplicate Post",
            summary="Summary",
            content="Content",
            clean_url="https://example.com/duplicate",
            embedding=embedding,
            is_duplicate=True,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        await post_repo.add(post1)
        await post_repo.add(post2)

        # Get duplicates
        duplicates = await post_repo.get_duplicates(limit=100)
        assert len(duplicates) == 1
        assert duplicates[0].is_duplicate is True
        assert duplicates[0].clean_url == "https://example.com/duplicate"
