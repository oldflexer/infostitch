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
    ) -> str:
        """Generate text content from prompt."""
        ...

    async def generate_embedding(self, text: str) -> Embedding:
        """Generate embedding for text."""
        ...

    async def generate_embeddings_batch(self, texts: List[str]) -> List[Embedding]:
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

    async def extract_content(self, url: str) -> str:
        """Extract main content from URL."""
        ...

    async def extract_with_options(
        self,
        url: str,
        timeout: int = 30,
        no_images: bool = False,
        no_links: bool = False,
    ) -> Dict[str, Any]:
        """Extract content with options."""
        ...

    async def extract_image_url(self, url: str) -> Optional[str]:
        """Extract featured image URL from page."""
        ...

    async def clean_content(self, content: str) -> str:
        """Clean extracted content."""
        ...

    async def close(self) -> None:
        """Close client connections."""
        ...


class PublisherClientProtocol(Protocol):
    """Protocol for publisher clients (Telegram, VK, Max)."""

    async def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = True,
    ) -> Dict[str, Any]:
        """Send text message."""
        ...

    async def send_photo(
        self,
        chat_id: str,
        photo_url: str,
        caption: Optional[str] = None,
        parse_mode: str = "HTML",
    ) -> Dict[str, Any]:
        """Send photo with optional caption."""
        ...

    async def send_document(
        self,
        chat_id: str,
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


class VKClientProtocol(PublisherClientProtocol):
    """Extended protocol for VK-specific features."""

    async def get_wall_upload_server(self, group_id: str) -> str:
        """Get upload server URL for wall photos."""
        ...

    async def upload_photo(self, upload_url: str, photo_path: str) -> Dict[str, Any]:
        """Upload photo to VK server."""
        ...

    async def save_wall_photo(
        self,
        group_id: str,
        photo: str,
        server: int,
        hash: str,
    ) -> Dict[str, Any]:
        """Save wall photo."""
        ...

    async def wall_post(
        self,
        owner_id: str,
        message: str,
        attachments: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Post to wall."""
        ...