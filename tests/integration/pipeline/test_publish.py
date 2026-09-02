"""Integration tests for PublishStep."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from application.dto.pipeline_context import PipelineContext
from domain.entities.post import Post
from domain.value_objects.embedding import Embedding


class TestPublishStep:
    """Tests for PublishStep (multi-channel publishing)."""

    @pytest.fixture
    def sample_final_posts(self):
        """Create sample final posts."""
        return [
            Post(
                id=1,
                title="AI Breakthrough",
                summary="Revolutionary AI model",
                content="🚀 AI Breakthrough! Revolutionary model...",
                clean_url="https://example.com/1",
                embedding=Embedding.from_list([0.1] * 768),
                image_url="https://example.com/image1.jpg",
                is_duplicate=False,
                source_id=1,
                template_id="news_brief",
            ),
            Post(
                id=2,
                title="Quantum Computing",
                summary="Quantum milestone",
                content="⚛️ Quantum Computing Milestone! ...",
                clean_url="https://example.com/2",
                embedding=Embedding.from_list([0.2] * 768),
                image_url=None,
                is_duplicate=False,
                source_id=2,
                template_id="tech_deep_dive",
            ),
        ]

    @pytest.fixture
    def mock_publisher_service(self):
        """Create a mock publisher service."""
        from application.services.publisher_service import PublisherService
        service = MagicMock(spec=PublisherService)
        service.publish_to_all = AsyncMock(side_effect=[
            {"telegram": {"success": True}, "vk": {"success": True}, "max": {"success": True}},
            {"telegram": {"success": True}, "vk": {"success": False, "error": "VK API error"}, "max": {"success": True}},
        ])
        return service

    @pytest.mark.asyncio
    async def test_publish_success(self, publish_step, sample_final_posts, mock_publisher_service):
        """Test successful publishing to all channels."""
        publish_step._publisher_service = mock_publisher_service

        context = PipelineContext(final_posts=sample_final_posts)

        result = await publish_step.execute(context)

        assert len(result.published_results) == 2
        assert result.metrics["published_count"] == 2

        # Check first post results
        result1 = result.published_results["https://example.com/1"]
        assert result1["telegram"]["success"] is True
        assert result1["vk"]["success"] is True
        assert result1["max"]["success"] is True

    @pytest.mark.asyncio
    async def test_publish_partial_failure(self, publish_step, sample_final_posts, mock_publisher_service):
        """Test publishing with partial channel failures."""
        publish_step._publisher_service = mock_publisher_service

        context = PipelineContext(final_posts=sample_final_posts)

        result = await publish_step.execute(context)

        # Second post has VK failure
        result2 = result.published_results["https://example.com/2"]
        assert result2["telegram"]["success"] is True
        assert result2["vk"]["success"] is False
        assert "error" in result2["vk"]

        # Should still count as published (at least one channel succeeded)
        assert result.metrics["published_count"] == 2

    @pytest.mark.asyncio
    async def test_publish_empty_input(self, publish_step, mock_publisher_service):
        """Test publishing with empty post list."""
        publish_step._publisher_service = mock_publisher_service

        context = PipelineContext(final_posts=[])

        result = await publish_step.execute(context)

        assert result.published_results == {}
        assert result.metrics["published_count"] == 0
        mock_publisher_service.publish_to_all.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_all_channels_fail(self, publish_step, sample_final_posts, mock_publisher_service):
        """Test when all channels fail for a post."""
        publish_step._publisher_service = mock_publisher_service
        mock_publisher_service.publish_to_all = AsyncMock(return_value={
            "telegram": {"success": False, "error": "Telegram error"},
            "vk": {"success": False, "error": "VK error"},
            "max": {"success": False, "error": "Max error"},
        })

        context = PipelineContext(final_posts=sample_final_posts[:1])

        result = await publish_step.execute(context)

        result1 = result.published_results["https://example.com/1"]
        assert all(not r["success"] for r in result1.values())
        # Post is counted as published because publish_to_all didn't throw an exception
        # (individual channel failures are not top-level errors)
        assert result.metrics["published_count"] == 1

    @pytest.mark.asyncio
    async def test_publish_service_error(self, publish_step, sample_final_posts, mock_publisher_service):
        """Test handling of publisher service errors."""
        publish_step._publisher_service = mock_publisher_service
        mock_publisher_service.publish_to_all = AsyncMock(side_effect=Exception("Network error"))

        context = PipelineContext(final_posts=sample_final_posts[:1])

        result = await publish_step.execute(context)

        assert len(result.errors) == 1
        assert "publish" in result.errors[0]
        assert "Network error" in result.errors[0]
        assert "error" in result.published_results["https://example.com/1"]