"""Integration tests for PublisherService."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from application.services.publisher_service import PublisherService


class TestPublisherService:
    """Tests for PublisherService."""

    @pytest.mark.asyncio
    async def test_publish_to_all(self, publisher_service):
        """Test publishing to all enabled channels."""
        text = "Test post content"
        image_url = "https://example.com/image.jpg"

        result = await publisher_service.publish_to_all(
            text=text,
            image_url=image_url,
        )

        assert isinstance(result, dict)
        # In test env, all three mock publishers should be enabled
        assert "telegram" in result
        assert "vk" in result
        assert "max" in result

        for channel_result in result.values():
            assert "success" in channel_result
            if channel_result["success"]:
                assert "result" in channel_result
            else:
                assert "error" in channel_result

    @pytest.mark.asyncio
    async def test_publish_to_all_no_image(self, publisher_service):
        """Test publishing without image."""
        text = "Test post without image"

        result = await publisher_service.publish_to_all(
            text=text,
            image_url=None,
        )

        assert isinstance(result, dict)
        assert "telegram" in result
        assert "vk" in result
        assert "max" in result

    @pytest.mark.asyncio
    async def test_get_publisher(self, publisher_service):
        """Test getting specific publisher."""
        tg_publisher = publisher_service.get_publisher("telegram")
        assert tg_publisher is not None

        vk_publisher = publisher_service.get_publisher("vk")
        assert vk_publisher is not None

        max_publisher = publisher_service.get_publisher("max")
        assert max_publisher is not None

        # Unknown channel
        unknown = publisher_service.get_publisher("unknown")
        assert unknown is None

    @pytest.mark.asyncio
    async def test_get_enabled_publishers(self, publisher_service):
        """Test getting all enabled publishers."""
        publishers = publisher_service.get_enabled_publishers()
        assert isinstance(publishers, list)
        assert len(publishers) == 3  # telegram, vk, max in test env

    @pytest.mark.asyncio
    async def test_close(self, publisher_service):
        """Test closing all publishers."""
        await publisher_service.close()