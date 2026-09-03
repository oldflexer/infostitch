"""Image Service.

Handles image extraction and processing from articles.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from infrastructure.clients.jina_client import JinaClient, MockJinaClient
from infrastructure.config import get_settings


class ImageService:
    """Service for extracting and processing images from articles."""

    def __init__(self, client: Optional[JinaClient] = None):
        self._client = client or self._create_default_client()

    def _create_default_client(self) -> JinaClient:
        settings = get_settings()
        if settings.app_env == "development" and not settings.jina_api_key:
            return MockJinaClient()
        return JinaClient()

    async def extract_content_and_image(
        self,
        url: str,
    ) -> Dict[str, Any]:
        """Extract full article content and image from URL.

        Args:
            url: Article URL

        Returns:
            Dict with 'title', 'content', 'description', 'image_url', 'url'
        """
        data = await self._client.extract_content(url)

        # Extract image
        image_url = self._client.extract_image_url(data)

        # Clean content
        content = data.get("content", "")
        cleaned_content = self._client.clean_content(content)

        return {
            "title": data.get("title", ""),
            "content": cleaned_content,
            "description": data.get("description", ""),
            "image_url": image_url,
            "url": url,
        }

    async def close(self) -> None:
        await self._client.close()
