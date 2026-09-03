"""Integration tests for ComputeEmbeddingStep."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from application.dto.pipeline_context import PipelineContext
from domain.value_objects.embedding import Embedding


class TestComputeEmbeddingStep:
    """Tests for ComputeEmbeddingStep (embedding generation)."""

    @pytest.fixture
    def sample_generated_posts(self):
        """Create sample generated posts."""
        return [{"article_id": 1,
                 "source_id": 1,
                 "title": "AI Breakthrough",
                 "summary": "Revolutionary AI model achieves human-level reasoning",
                 "post_text": "🚀 AI Breakthrough! Revolutionary model...",
                 "template_id": "news_brief",
                 "clean_url": "https://example.com/1",
                 "image_url": "https://example.com/image1.jpg",
                 },
                {"article_id": 2,
                 "source_id": 2,
                 "title": "Quantum Computing",
                 "summary": "Quantum computer solves impossible problem",
                 "post_text": "⚛️ Quantum Computing Milestone! ...",
                 "template_id": "tech_deep_dive",
                 "clean_url": "https://example.com/2",
                 "image_url": None,
                 },
                ]

    @pytest.fixture
    def mock_embedding_service(self):
        """Create a mock embedding service."""
        from application.services.embedding_service import EmbeddingService
        service = MagicMock(spec=EmbeddingService)
        # Return 768-dimensional embeddings
        service.generate_embedding = AsyncMock(side_effect=[
            [0.1] * 768,
            [0.2] * 768,
        ])
        return service

    @pytest.mark.asyncio
    async def test_compute_embedding_success(
            self,
            compute_embedding_step,
            sample_generated_posts,
            mock_embedding_service):
        """Test successful embedding computation."""
        compute_embedding_step._embedding_service = mock_embedding_service

        context = PipelineContext(generated_posts=sample_generated_posts)

        result = await compute_embedding_step.execute(context)

        assert len(result.post_embeddings) == 2
        assert result.metrics["embeddings_computed"] == 2

        # Check embeddings are Embedding objects
        assert isinstance(result.post_embeddings[0], Embedding)
        assert isinstance(result.post_embeddings[1], Embedding)
        assert len(result.post_embeddings[0].vector) == 768
        assert len(result.post_embeddings[1].vector) == 768

    @pytest.mark.asyncio
    async def test_compute_embedding_empty_input(
            self, compute_embedding_step, mock_embedding_service):
        """Test embedding computation with empty input."""
        compute_embedding_step._embedding_service = mock_embedding_service

        context = PipelineContext(generated_posts=[])

        result = await compute_embedding_step.execute(context)

        assert result.post_embeddings == []
        assert result.metrics["embeddings_computed"] == 0
        mock_embedding_service.generate_embedding.assert_not_called()

    @pytest.mark.asyncio
    async def test_compute_embedding_handles_errors(
            self,
            compute_embedding_step,
            sample_generated_posts,
            mock_embedding_service):
        """Test handling of embedding generation errors."""
        compute_embedding_step._embedding_service = mock_embedding_service
        mock_embedding_service.generate_embedding = AsyncMock(side_effect=[
            [0.1] * 768,
            Exception("Embedding service timeout"),
        ])

        context = PipelineContext(generated_posts=sample_generated_posts)

        result = await compute_embedding_step.execute(context)

        assert len(result.post_embeddings) == 2
        assert len(result.errors) == 1
        assert "compute_embedding" in result.errors[0]
        assert "Embedding service timeout" in result.errors[0]

        # Second embedding should be zero vector (fallback)
        assert isinstance(result.post_embeddings[1], Embedding)
        assert all(v == 0.0 for v in result.post_embeddings[1].vector)

    @pytest.mark.asyncio
    async def test_compute_embedding_all_fail(
            self,
            compute_embedding_step,
            sample_generated_posts,
            mock_embedding_service):
        """Test when all embedding generations fail."""
        compute_embedding_step._embedding_service = mock_embedding_service
        mock_embedding_service.generate_embedding = AsyncMock(
            side_effect=Exception("Service down"))

        context = PipelineContext(generated_posts=sample_generated_posts)

        result = await compute_embedding_step.execute(context)

        assert len(result.post_embeddings) == 2
        assert len(result.errors) == 2
        # Both should be zero vectors
        for emb in result.post_embeddings:
            assert all(v == 0.0 for v in emb.vector)
