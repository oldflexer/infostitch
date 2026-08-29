"""Channel Repository Interface.

Defines the contract for channel data access.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.channel import Channel


class ChannelRepository(ABC):
    """Abstract repository for Channel entities."""

    @abstractmethod
    async def add(self, channel: Channel) -> Channel:
        """Add a new channel."""
        ...

    @abstractmethod
    async def get_by_id(self, channel_id: int) -> Optional[Channel]:
        """Get channel by ID."""
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Channel]:
        """Get channel by name."""
        ...

    @abstractmethod
    async def get_all(self, enabled_only: bool = False) -> List[Channel]:
        """Get all channels."""
        ...

    @abstractmethod
    async def get_enabled(self) -> List[Channel]:
        """Get only enabled channels."""
        ...

    @abstractmethod
    async def get_by_type(self, channel_type: str) -> List[Channel]:
        """Get channels by type."""
        ...

    @abstractmethod
    async def update(self, channel: Channel) -> Channel:
        """Update an existing channel."""
        ...

    @abstractmethod
    async def delete(self, channel_id: int) -> bool:
        """Delete a channel."""
        ...

    @abstractmethod
    async def count(self) -> int:
        """Count total channels."""
        ...