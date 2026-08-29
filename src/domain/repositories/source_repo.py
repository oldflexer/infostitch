"""Source Repository Interface.

Defines the contract for RSS source data access.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.rss_source import RssSource


class SourceRepository(ABC):
    """Abstract repository for RssSource entities."""

    @abstractmethod
    async def add(self, source: RssSource) -> RssSource:
        """Add a new RSS source."""
        ...

    @abstractmethod
    async def get_by_id(self, source_id: int) -> Optional[RssSource]:
        """Get source by ID."""
        ...

    @abstractmethod
    async def get_by_url(self, url: str) -> Optional[RssSource]:
        """Get source by URL."""
        ...

    @abstractmethod
    async def get_all(self, enabled_only: bool = False) -> List[RssSource]:
        """Get all sources."""
        ...

    @abstractmethod
    async def get_enabled(self) -> List[RssSource]:
        """Get only enabled sources."""
        ...

    @abstractmethod
    async def update(self, source: RssSource) -> RssSource:
        """Update an existing source."""
        ...

    @abstractmethod
    async def delete(self, source_id: int) -> bool:
        """Delete a source."""
        ...

    @abstractmethod
    async def update_last_fetch(self, source_id: int) -> bool:
        """Update last_fetch timestamp."""
        ...

    @abstractmethod
    async def count(self) -> int:
        """Count total sources."""
        ...