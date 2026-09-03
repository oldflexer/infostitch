"""Integration tests for CheckEmbeddingDuplicateStep."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from application.dto.pipeline_context import PipelineContext
from domain.value_objects.embedding import Embedding


class TestCheckEmbeddingDuplicateStep:
    """Tests for CheckEmbeddingDuplicateStep (Stage 2: semantic dedup)."""

    @pytest.fixture
    def sample_generated_posts(self):
        """Create sample generated posts."""
        return [
            {
                "article_id": 1,
                "source_id": 1,
                "title": "AI Breakthrough",
                "summary": "Revolutionary AI model",
                "post_text": "🚀 AI Breakthrough! ...",
                "template_id": "news_brief",
                "clean_url": "https://example.com/1",
                "image_url": "https://example.com/image1.jpg",
            },
            {
                "article_id": 2,
                "source_id": 2,
                "title": "Quantum Computing",
                "summary": "Quantum milestone",
                "post_text": "⚛️ Quantum Computing! ...",
                "template_id": "tech_deep_dive",
                "clean_url": "https://example.com/2",
                "image_url": None,
            },
        ]

    @pytest.fixture
    def sample_embeddings(self):
        """Create sample embeddings."""
        return [
            Embedding.from_list([0.1] * 768),
            Embedding.from_list([0.2] * 768),
        ]

    @pytest.fixture
    def mock_dedup_service(self):
        """Create a mock deduplication service."""
        from application.services.deduplication_service import DeduplicationService
        service = MagicMock(spec=DeduplicationService)
        service.is_duplicate_by_embedding = AsyncMock(
            side_effect=[False, True])
        return service

    @pytest.mark.asyncio
    async def test_check_embedding_duplicate_mixed(
            self,
            check_embedding_duplicate_step,
            sample_generated_posts,
            sample_embeddings,
            mock_dedup_service):
        """Test semantic duplicate check with mixed results."""
        check_embedding_duplicate_step._dedup_service = mock_dedup_service

        context = PipelineContext(
            generated_posts=sample_generated_posts,
            post_embeddings=sample_embeddings,
        )

        result = await check_embedding_duplicate_step.execute(context)

        assert len(result.final_posts) == 1
        assert len(result.duplicate_posts) == 1
        assert result.metrics["final_posts"] == 1
        assert result.metrics["duplicate_posts"] == 1

        final_post = result.final_posts[0]
        assert final_post.clean_url == "https://example.com/1"
        assert final_post.is_duplicate is False

        dup_post = result.duplicate_posts[0]
        assert dup_post.clean_url == "https://example.com/2"
        assert dup_post.is_duplicate is True

    @pytest.mark.asyncio
    async def test_check_embedding_duplicate_all_unique(
            self,
            check_embedding_duplicate_step,
            sample_generated_posts,
            sample_embeddings,
            mock_dedup_service):
        """Test when all posts are unique."""
        check_embedding_duplicate_step._dedup_service = mock_dedup_service
        mock_dedup_service.is_duplicate_by_embedding = AsyncMock(
            return_value=False)

        context = PipelineContext(
            generated_posts=sample_generated_posts,
            post_embeddings=sample_embeddings,
        )

        result = await check_embedding_duplicate_step.execute(context)

        assert len(result.final_posts) == 2
        assert len(result.duplicate_posts) == 0
        assert result.metrics["final_posts"] == 2
        assert result.metrics["duplicate_posts"] == 0

    @pytest.mark.asyncio
    async def test_check_embedding_duplicate_all_duplicates(
            self,
            check_embedding_duplicate_step,
            sample_generated_posts,
            sample_embeddings,
            mock_dedup_service):
        """Test when all posts are duplicates."""
        check_embedding_duplicate_step._dedup_service = mock_dedup_service
        mock_dedup_service.is_duplicate_by_embedding = AsyncMock(
            return_value=True)

        context = PipelineContext(
            generated_posts=sample_generated_posts,
            post_embeddings=sample_embeddings,
        )

        result = await check_embedding_duplicate_step.execute(context)

        assert len(result.final_posts) == 0
        assert len(result.duplicate_posts) == 2
        assert result.metrics["final_posts"] == 0
        assert result.metrics["duplicate_posts"] == 2

    @pytest.mark.asyncio
    async def test_check_embedding_duplicate_empty_input(
            self, check_embedding_duplicate_step, mock_dedup_service):
        """Test with empty input."""
        check_embedding_duplicate_step._dedup_service = mock_dedup_service

        context = PipelineContext(generated_posts=[], post_embeddings=[])

        result = await check_embedding_duplicate_step.execute(context)

        assert result.final_posts == []
        assert result.duplicate_posts == []
        assert result.metrics["final_posts"] == 0
        assert result.metrics["duplicate_posts"] == 0
        mock_dedup_service.is_duplicate_by_embedding.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_embedding_duplicate_error_handled(
            self,
            check_embedding_duplicate_step,
            sample_generated_posts,
            sample_embeddings,
            mock_dedup_service):
        """Test handling of service errors."""
        check_embedding_duplicate_step._dedup_service = mock_dedup_service
        mock_dedup_service.is_duplicate_by_embedding = AsyncMock(side_effect=[
            False,
            Exception("DB connection error"),
        ])

        context = PipelineContext(
            generated_posts=sample_generated_posts,
            post_embeddings=sample_embeddings,
        )

        result = await check_embedding_duplicate_step.execute(context)

        assert len(result.errors) == 1
        assert "check_embedding_duplicate" in result.errors[0]
        assert "DB connection error" in result.errors[0]
