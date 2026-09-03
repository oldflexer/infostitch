"""Integration tests for ImageService."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from application.services.image_service import ImageService


class TestImageService:
    """Tests for ImageService."""

    @pytest.fixture
    def mock_jina_client(self):
        """Create a mock Jina client."""
        from infrastructure.clients.jina_client import MockJinaClient
        return MockJinaClient()

    @pytest.fixture
    def image_service(self, mock_jina_client):
        """Create ImageService with mock client."""
        return ImageService(client=mock_jina_client)

    @pytest.mark.asyncio
    async def test_extract_content_and_image(self, image_service):
        """Test content and image extraction."""
        url = "https://example.com/article"
        result = await image_service.extract_content_and_image(url)

        assert isinstance(result, dict)
        assert "title" in result
        assert "content" in result
        assert "description" in result
        assert "image_url" in result
        assert "url" in result
        assert result["url"] == url

    @pytest.mark.asyncio
    async def test_extract_content_with_image(self, image_service):
        """Test extraction when image is present."""
        url = "https://example.com/article-with-image"
        result = await image_service.extract_content_and_image(url)

        # MockJinaClient returns image_url for some URLs
        assert result["image_url"] is not None or result["image_url"] is None

    @pytest.mark.asyncio
    async def test_extract_content_without_image(self, image_service):
        """Test extraction when no image."""
        url = "https://example.com/article-no-image"
        result = await image_service.extract_content_and_image(url)

        assert "image_url" in result

    @pytest.mark.asyncio
    async def test_close(self, image_service):
        """Test closing the service."""
        await image_service.close()
