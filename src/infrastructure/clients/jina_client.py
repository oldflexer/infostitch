"""Jina AI Reader Client.

Provides async interface to Jina AI Reader API for content extraction.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from infrastructure.config import get_settings


class JinaClient:
    """Async client for Jina AI Reader API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://r.jina.ai",
    ):
        self._api_key = api_key or get_settings().jina_api_key
        self._base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=10.0),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "application/json",
        }
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    @retry(
        wait=wait_exponential_jitter(initial=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def extract_content(self, url: str) -> Dict[str, Any]:
        """Extract full article content from URL.

        Args:
            url: Article URL to extract

        Returns:
            Dict with 'title', 'content', 'description', 'image', 'url'
        """
        extract_url = f"{self._base_url}/http://{url.lstrip('https://').lstrip('http://')}"

        response = await self.client.get(
            extract_url,
            headers=self._get_headers(),
        )
        response.raise_for_status()

        data = response.json()
        return data.get("data", {})

    @retry(
        wait=wait_exponential_jitter(initial=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def extract_with_options(
        self,
        url: str,
        timeout: int = 30,
        with_generated_alt: bool = True,
        with_images_summary: bool = True,
    ) -> Dict[str, Any]:
        """Extract content with additional options.

        Args:
            url: Article URL
            timeout: Request timeout in seconds
            with_generated_alt: Generate alt text for images
            with_images_summary: Include images summary

        Returns:
            Full extraction result
        """
        params = {
            "timeout": timeout,
            "with_generated_alt": str(with_generated_alt).lower(),
            "with_images_summary": str(with_images_summary).lower(),
        }

        extract_url = f"{self._base_url}/http://{url.lstrip('https://').lstrip('http://')}"

        response = await self.client.get(
            extract_url,
            headers=self._get_headers(),
            params=params,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("data", {})

    def extract_image_url(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract best image URL from Jina response.

        Priority: featured image > first image in content > None
        """
        # Check for featured image
        if data.get("image"):
            return data["image"]

        # Check for images in content
        images = data.get("images", [])
        if images:
            return images[0].get("url") if isinstance(images[0], dict) else images[0]

        # Try to extract from markdown content
        content = data.get("content", "")
        img_match = re.search(r'!\[.*?\]\((https?://[^\s)]+)\)', content)
        if img_match:
            return img_match.group(1)

        return None

    def clean_content(self, content: str, max_length: int = 6000) -> str:
        """Clean extracted content.

        Removes links, images, extra newlines, truncates to max_length.
        """
        # Remove markdown links but keep text
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)

        # Remove markdown images
        content = re.sub(r'!\[.*?\]\([^)]+\)', '', content)

        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)

        # Normalize whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r' {2,}', ' ', content)

        # Truncate
        if len(content) > max_length:
            content = content[:max_length].rsplit(' ', 1)[0] + '...'

        return content.strip()


class MockJinaClient:
    """Mock Jina client for testing."""

    def __init__(self, *args, **kwargs):
        self.call_count = 0

    async def close(self) -> None:
        pass

    async def extract_content(self, url: str) -> Dict[str, Any]:
        self.call_count += 1
        return {
            "title": "Test Article Title",
            "content": "This is the full article content extracted by Jina AI. " * 10,
            "description": "Test article description",
            "image": "https://example.com/image.jpg",
            "url": url,
        }

    async def extract_with_options(
        self,
        url: str,
        timeout: int = 30,
        with_generated_alt: bool = True,
        with_images_summary: bool = True,
    ) -> Dict[str, Any]:
        return await self.extract_content(url)

    def extract_image_url(self, data: Dict[str, Any]) -> Optional[str]:
        return data.get("image")

    def clean_content(self, content: str, max_length: int = 6000) -> str:
        return content[:max_length]