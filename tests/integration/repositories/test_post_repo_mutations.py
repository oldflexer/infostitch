"""Integration tests for PostRepository - Mutation methods."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta

from domain.entities.post import Post
from domain.value_objects.embedding import Embedding


class TestPostRepositoryMutations:
    """Integration tests for SqlAlchemyPostRepository mutation methods."""

    @pytest.mark.asyncio
    async def test_update_post(self, post_repo):
        """Test updating a post."""
        embedding = Embedding.from_list([0.1] * 768)
        now = datetime.now(timezone.utc)

        post = Post(
            id=None,
            title="Original Title",
            summary="Original summary",
            content="Original content",
            clean_url="https://example.com/update",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        added = await post_repo.add(post)

        # Update the post
        added.title = "Updated Title"
        added.summary = "Updated summary"
        updated = await post_repo.update(added)

        assert updated.title == "Updated Title"
        assert updated.summary == "Updated summary"

        # Verify in database
        retrieved = await post_repo.get_by_id(added.id)
        assert retrieved.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_delete_post(self, post_repo):
        """Test deleting a post."""
        embedding = Embedding.from_list([0.1] * 768)
        now = datetime.now(timezone.utc)

        post = Post(
            id=None,
            title="To Delete",
            summary="Summary",
            content="Content",
            clean_url="https://example.com/delete",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        added = await post_repo.add(post)

        # Delete
        result = await post_repo.delete(added.id)
        assert result is True

        # Verify deleted
        retrieved = await post_repo.get_by_id(added.id)
        assert retrieved is None

        # Delete non-existent
        result = await post_repo.delete(99999)
        assert result is False

    @pytest.mark.asyncio
    async def test_count_recent(self, post_repo):
        """Test counting recent posts."""
        embedding = Embedding.from_list([0.1] * 768)
        now = datetime.now(timezone.utc)

        # Add 3 recent posts
        for i in range(3):
            post = Post(
                id=None,
                title=f"Post {i}",
                summary="Summary",
                content="Content",
                clean_url=f"https://example.com/count{i}",
                embedding=embedding,
                is_duplicate=False,
                source_id=1,
                channel_id=1,
                llm_model_id=1,
                template_id="news_brief",
                created_at=now,
            )
            await post_repo.add(post)

        # Add 1 duplicate (should not count)
        post_dup = Post(
            id=None,
            title="Duplicate",
            summary="Summary",
            content="Content",
            clean_url="https://example.com/dup",
            embedding=embedding,
            is_duplicate=True,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        await post_repo.add(post_dup)

        count = await post_repo.count_recent(days=5)
        assert count == 3

    @pytest.mark.asyncio
    async def test_cleanup_old(self, post_repo):
        """Test cleaning up old posts."""
        embedding = Embedding.from_list([0.1] * 768)
        now = datetime.now(timezone.utc)

        # Add recent post
        post1 = Post(
            id=None,
            title="Recent Post",
            summary="Summary",
            content="Content",
            clean_url="https://example.com/recent",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        # Add old post (100 days ago)
        post2 = Post(
            id=None,
            title="Old Post",
            summary="Summary",
            content="Content",
            clean_url="https://example.com/old",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now - timedelta(days=100),
        )
        await post_repo.add(post1)
        await post_repo.add(post2)

        # Cleanup posts older than 90 days
        deleted = await post_repo.cleanup_old(days=90)
        assert deleted == 1

        # Verify old post deleted, recent remains
        retrieved = await post_repo.get_by_clean_url("https://example.com/old")
        assert retrieved is None

        retrieved = await post_repo.get_by_clean_url("https://example.com/recent")
        assert retrieved is not None
