"""Integration tests for ExtractContentStep."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from application.dto.pipeline_context import PipelineContext
from domain.entities.article import Article
from domain.value_objects.url import URL


class TestExtractContentStep:
    """Tests for ExtractContentStep (Jina AI content extraction)."""

    @pytest.fixture
    def sample_selected_articles(self):
        """Create sample selected articles."""
        return [
            Article(
                id=1,
                title="AI Breakthrough",
                url=URL("https://example.com/1"),
                summary="Summary 1",
                source_id=1,
            ),
            Article(
                id=2,
                title="Quantum Computing",
                url=URL("https://example.com/2"),
                summary="Summary 2",
                source_id=2,
            ),
        ]

    @pytest.fixture
    def mock_image_service(self):
        """Create a mock image service."""
        from application.services.image_service import ImageService
        service = MagicMock(spec=ImageService)
        service.extract_content_and_image = AsyncMock(side_effect=[
            {
                "title": "AI Breakthrough",
                "description": "Full content about AI breakthrough...",
                "content": "Full article content here...",
                "image_url": "https://example.com/image1.jpg",
                "url": "https://example.com/1",
            },
            {
                "title": "Quantum Computing",
                "description": "Full content about quantum computing...",
                "content": "Full article content here...",
                "image_url": None,
                "url": "https://example.com/2",
            },
        ])
        return service

    @pytest.mark.asyncio
    async def test_extract_content_success(self, extract_content_step, sample_selected_articles, mock_image_service):
        """Test successful content extraction."""
        extract_content_step._image_service = mock_image_service

        context = PipelineContext(selected_articles=sample_selected_articles)

        result = await extract_content_step.execute(context)

        assert len(result.extracted_articles) == 2
        assert result.metrics["extracted_count"] == 2

        # Check first article
        extracted1 = result.extracted_articles[0]
        assert extracted1["article_id"] == 1
        assert extracted1["source_id"] == 1
        assert extracted1["original_title"] == "AI Breakthrough"
        assert extracted1["image_url"] == "https://example.com/image1.jpg"

        # Check second article (no image)
        extracted2 = result.extracted_articles[1]
        assert extracted2["article_id"] == 2
        assert extracted2["image_url"] is None

    @pytest.mark.asyncio
    async def test_extract_content_empty_input(self, extract_content_step, mock_image_service):
        """Test extraction with empty article list."""
        extract_content_step._image_service = mock_image_service

        context = PipelineContext(selected_articles=[])

        result = await extract_content_step.execute(context)

        assert result.extracted_articles == []
        assert result.metrics["extracted_count"] == 0
        mock_image_service.extract_content_and_image.assert_not_called()

    @pytest.mark.asyncio
    async def test_extract_content_handles_errors(self, extract_content_step, sample_selected_articles, mock_image_service):
        """Test handling of extraction errors."""
        extract_content_step._image_service = mock_image_service
        # First call succeeds, second fails
        mock_image_service.extract_content_and_image = AsyncMock(side_effect=[
            {
                "title": "AI Breakthrough",
                "description": "Content...",
                "content": "Full content...",
                "image_url": "https://example.com/image1.jpg",
                "url": "https://example.com/1",
            },
            Exception("Jina API timeout"),
        ])

        context = PipelineContext(selected_articles=sample_selected_articles)

        result = await extract_content_step.execute(context)

        # Should have 1 successful extraction, 1 error
        assert len(result.extracted_articles) == 1
        assert len(result.errors) == 1
        assert "extract_content" in result.errors[0]
        assert "Jina API timeout" in result.errors[0]
        assert result.metrics["extracted_count"] == 1

    @pytest.mark.asyncio
    async def test_extract_content_all_fail(self, extract_content_step, sample_selected_articles, mock_image_service):
        """Test when all extractions fail."""
        extract_content_step._image_service = mock_image_service
        mock_image_service.extract_content_and_image = AsyncMock(side_effect=Exception("Service unavailable"))

        context = PipelineContext(selected_articles=sample_selected_articles)

        result = await extract_content_step.execute(context)

        assert result.extracted_articles == []
        assert len(result.errors) == 2
        assert result.metrics["extracted_count"] == 0