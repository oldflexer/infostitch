"""Article Repository Interface.

Defines the contract for article data access.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.article import Article


class ArticleRepository(ABC):
    """Abstract repository for Article entities."""

    @abstractmethod
    async def add(self, article: Article) -> Article:
        """Add a new article."""
        ...

    @abstractmethod
    async def get_by_id(self, article_id: int) -> Optional[Article]:
        """Get article by ID."""
        ...

    @abstractmethod
    async def get_by_url(self, url: str) -> Optional[Article]:
        """Get article by URL."""
        ...

    @abstractmethod
    async def get_by_source(
        self, source_id: int, limit: int = 100
    ) -> List[Article]:
        """Get articles by source ID."""
        ...

    @abstractmethod
    async def get_recent(self, hours: int = 24, limit: int = 100) -> List[Article]:
        """Get recent articles."""
        ...

    @abstractmethod
    async def get_unprocessed(self, limit: int = 100) -> List[Article]:
        """Get articles that haven't been processed yet."""
        ...

    @abstractmethod
    async def update(self, article: Article) -> Article:
        """Update an existing article."""
        ...

    @abstractmethod
    async def delete(self, article_id: int) -> bool:
        """Delete an article."""
        ...

    @abstractmethod
    async def exists_by_url(self, url: str) -> bool:
        """Check if article exists by URL."""
        ...

    @abstractmethod
    async def count_by_source(self, source_id: int) -> int:
        """Count articles by source."""
        ...