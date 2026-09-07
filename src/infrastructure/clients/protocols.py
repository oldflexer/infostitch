"""Protocol definitions for client interfaces.

These protocols define the expected interface for external API clients,
allowing both real implementations and mocks to be used interchangeably.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol
from domain.value_objects.embedding import Embedding


class LLMClientProtocol(Protocol):
    """Protocol for LLM API clients (Gemini, etc.)."""

    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        response_mime_type: str = "text/plain",
    ) -> str:
        """Generate text content from prompt."""
        ...

    async def generate_embedding(
        self,
        text: str,
        model: str = "text-embedding-004",
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> Embedding:
        """Generate embedding for text."""
        ...

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        model: str = "text-embedding-004",
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> List[Embedding]:
        """Generate embeddings for multiple texts."""
        ...

    async def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        ...

    async def close(self) -> None:
        """Close client connections."""
        ...


class ContentExtractionClientProtocol(Protocol):
    """Protocol for content extraction clients (Jina AI, etc.)."""

    async def extract_content(self, url: str) -> Dict[str, Any]:
        """Extract main content from URL."""
        ...

    async def extract_with_options(
        self,
        url: str,
        timeout: int = 30,
        with_generated_alt: bool = True,
        with_images_summary: bool = True,
    ) -> Dict[str, Any]:
        """Extract content with options."""
        ...

    async def extract_image_url(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract featured image URL from page."""
        ...

    async def clean_content(self, content: str, max_length: int = 6000) -> str:
        """Clean extracted content."""
        ...

    async def close(self) -> None:
        """Close client connections."""
        ...


class PublisherClientProtocol(Protocol):
    """Protocol for publisher clients (Telegram, Max)."""

    async def send_message(
        self,
        text: str,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = True,
    ) -> Dict[str, Any]:
        """Send text message."""
        ...

    async def send_photo(
        self,
        photo_url: str,
        caption: Optional[str] = None,
        parse_mode: str = "HTML",
    ) -> Dict[str, Any]:
        """Send photo with optional caption."""
        ...

    async def send_document(
        self,
        document_url: str,
        caption: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send document."""
        ...

    async def get_me(self) -> Dict[str, Any]:
        """Get bot info."""
        ...

    async def close(self) -> None:
        """Close client connections."""
        ...


class VKClientProtocol(Protocol):
    """Protocol for VK-specific features."""

    async def get_wall_upload_server(self, group_id: str) -> Dict[str, Any]:
        """Get upload server URL for wall photos."""
        ...

    async def upload_photo(self, upload_url: str, photo_path: str) -> Dict[str, Any]:
        """Upload photo to VK server."""
        ...

    async def save_wall_photo(
        self,
        group_id: str,
        server: int,
        photo: str,
        hash: str,
    ) -> List[Dict[str, Any]]:
        """Save wall photo."""
        ...

    async def wall_post(
        self,
        message: str,
        attachments: Optional[str] = None,
        from_group: bool = True,
    ) -> Dict[str, Any]:
        """Post to wall."""
        ...

    async def post_with_photo(
        self,
        message: str,
        photo_url: str,
    ) -> Dict[str, Any]:
        """Download photo, upload to VK, and post to wall."""
        ...

    async def close(self) -> None:
        """Close client connections."""
        ...
"""Protocol definitions for client interfaces.

These protocols define the expected interface for external API clients,
allowing both real implementations and mocks to be used interchangeably.
"""