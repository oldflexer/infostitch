"""Integration tests for PostRepository - Similarity search."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta

from domain.entities.post import Post
from domain.value_objects.embedding import Embedding


class TestPostRepositorySimilarity:
    """Integration tests for SqlAlchemyPostRepository similarity search."""

    @pytest.mark.asyncio
    async def test_find_similar_embedding(self, post_repo):
        """Test finding similar post by embedding."""
        # Create base embedding
        base_vector = [0.1] * 768
        base_vector[0] = 0.9
        base_norm = sum(v * v for v in base_vector) ** 0.5
        base_vector = [v / base_norm for v in base_vector]

        # Create similar embedding (cosine similarity ~0.95)
        similar_vector = base_vector.copy()
        similar_vector[1] = 0.2
        similar_norm = sum(v * v for v in similar_vector) ** 0.5
        similar_vector = [v / similar_norm for v in similar_vector]

        # Create different embedding (low similarity)
        different_vector = [0.0] * 768
        different_vector[2] = 1.0
        different_norm = sum(v * v for v in different_vector) ** 0.5
        different_vector = [v / different_norm for v in different_vector]

        now = datetime.now(timezone.utc)

        # Add base post
        post1 = Post(
            id=None,
            title="Original Post",
            summary="Original summary",
            content="Original content",
            clean_url="https://example.com/original",
            embedding=Embedding.from_list(base_vector),
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        await post_repo.add(post1)

        # Add different post
        post2 = Post(
            id=None,
            title="Different Post",
            summary="Different summary",
            content="Different content",
            clean_url="https://example.com/different",
            embedding=Embedding.from_list(different_vector),
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        await post_repo.add(post2)

        # Search with similar embedding - should find post1
        similar = await post_repo.find_similar(
            embedding=Embedding.from_list(similar_vector),
            threshold=0.75,
            days=5,
        )
        assert similar is not None
        assert similar.clean_url == "https://example.com/original"

        # Search with different embedding - should not find anything
        # Create a vector that's different from BOTH base_vector and different_vector
        # Use index 3 = 1.0 (different from index 0=0.9 in base and index 2=1.0
        # in different)
        truly_different_vector = [0.0] * 768
        truly_different_vector[3] = 1.0
        truly_different_norm = sum(
            v * v for v in truly_different_vector) ** 0.5
        truly_different_vector = [
            v / truly_different_norm for v in truly_different_vector]

        similar = await post_repo.find_similar(
            embedding=Embedding.from_list(truly_different_vector),
            threshold=0.75,
            days=5,
        )
        assert similar is None

    @pytest.mark.asyncio
    async def test_find_similar_excludes_duplicates(self, post_repo):
        """Test that find_similar excludes duplicate posts."""
        base_vector = [0.1] * 768
        base_vector[0] = 0.9
        base_norm = sum(v * v for v in base_vector) ** 0.5
        base_vector = [v / base_norm for v in base_vector]

        now = datetime.now(timezone.utc)

        # Add duplicate post
        post1 = Post(
            id=None,
            title="Duplicate Post",
            summary="Duplicate summary",
            content="Duplicate content",
            clean_url="https://example.com/duplicate",
            embedding=Embedding.from_list(base_vector),
            is_duplicate=True,  # Marked as duplicate
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        await post_repo.add(post1)

        # Search should not find duplicate posts
        similar = await post_repo.find_similar(
            embedding=Embedding.from_list(base_vector),
            threshold=0.75,
            days=5,
        )
        assert similar is None
