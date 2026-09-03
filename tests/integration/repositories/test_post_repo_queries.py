"""Integration tests for PostRepository - Query methods."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta

from domain.entities.post import Post
from domain.value_objects.embedding import Embedding


class TestPostRepositoryQueries:
    """Integration tests for SqlAlchemyPostRepository query methods."""

    @pytest.mark.asyncio
    async def test_get_recent(self, post_repo):
        """Test getting recent posts."""
        embedding = Embedding.from_list([0.1] * 768)
        now = datetime.now(timezone.utc)

        # Add recent post
        post1 = Post(
            id=None,
            title="Recent Post",
            summary="Recent summary",
            content="Recent content",
            clean_url="https://example.com/recent",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        await post_repo.add(post1)

        # Add old post (10 days ago)
        post2 = Post(
            id=None,
            title="Old Post",
            summary="Old summary",
            content="Old content",
            clean_url="https://example.com/old",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now - timedelta(days=10),
        )
        await post_repo.add(post2)

        # Get recent (5 days)
        recent = await post_repo.get_recent(days=5, limit=100)
        assert len(recent) == 1
        assert recent[0].clean_url == "https://example.com/recent"

        # Get recent (15 days)
        recent = await post_repo.get_recent(days=15, limit=100)
        assert len(recent) == 2

    @pytest.mark.asyncio
    async def test_get_recent_excludes_duplicates(self, post_repo):
        """Test that get_recent excludes duplicates by default."""
        embedding = Embedding.from_list([0.1] * 768)
        now = datetime.now(timezone.utc)

        # Add unique post
        post1 = Post(
            id=None,
            title="Unique Post",
            summary="Unique summary",
            content="Unique content",
            clean_url="https://example.com/unique",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        await post_repo.add(post1)

        # Add duplicate post
        post2 = Post(
            id=None,
            title="Duplicate Post",
            summary="Duplicate summary",
            content="Duplicate content",
            clean_url="https://example.com/duplicate",
            embedding=embedding,
            is_duplicate=True,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        await post_repo.add(post2)

        # Default should exclude duplicates
        recent = await post_repo.get_recent(days=5, limit=100)
        assert len(recent) == 1
        assert recent[0].clean_url == "https://example.com/unique"

        # With exclude_duplicates=False
        recent = await post_repo.get_recent(days=5, limit=100, exclude_duplicates=False)
        assert len(recent) == 2
