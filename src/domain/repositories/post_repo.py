"""Post Repository Interface.

Defines the contract for post data access.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.post import Post
from domain.value_objects.embedding import Embedding


class PostRepository(ABC):
    """Abstract repository for Post entities."""

    @abstractmethod
    async def add(self, post: Post) -> Post:
        """Add a new post."""
        ...

    @abstractmethod
    async def get_by_id(self, post_id: int) -> Optional[Post]:
        """Get post by ID."""
        ...

    @abstractmethod
    async def get_by_clean_url(self, clean_url: str) -> Optional[Post]:
        """Get post by clean URL (for deduplication)."""
        ...

    @abstractmethod
    async def exists_by_url(self, clean_url: str) -> bool:
        """Check if post exists by clean URL."""
        ...

    @abstractmethod
    async def get_recent(
        self, days: int = 5, limit: int = 100, exclude_duplicates: bool = True
    ) -> List[Post]:
        """Get recent posts."""
        ...

    @abstractmethod
    async def get_by_source(
        self, source_id: int, limit: int = 100
    ) -> List[Post]:
        """Get posts by source ID."""
        ...

    @abstractmethod
    async def get_by_channel(
        self, channel_id: int, limit: int = 100
    ) -> List[Post]:
        """Get posts by channel ID."""
        ...

    @abstractmethod
    async def get_duplicates(self, limit: int = 100) -> List[Post]:
        """Get posts marked as duplicates."""
        ...

    @abstractmethod
    async def update(self, post: Post) -> Post:
        """Update an existing post."""
        ...

    @abstractmethod
    async def delete(self, post_id: int) -> bool:
        """Delete a post."""
        ...

    @abstractmethod
    async def find_similar(
        self, embedding: Embedding, threshold: float = 0.75, days: int = 5
    ) -> Optional[Post]:
        """Find most similar post by embedding (semantic deduplication)."""
        ...

    @abstractmethod
    async def count_recent(self, days: int = 5) -> int:
        """Count recent posts."""
        ...

    @abstractmethod
    async def cleanup_old(self, days: int = 90) -> int:
        """Delete posts older than specified days. Returns count deleted."""
        ...