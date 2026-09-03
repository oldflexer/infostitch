"""Setting Repository Interface.

Defines the contract for settings data access.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class SettingRepository(ABC):
    """Abstract repository for settings."""

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get setting value by key."""
        ...

    @abstractmethod
    async def get_all(self) -> Dict[str, str]:
        """Get all settings as dictionary."""
        ...

    @abstractmethod
    async def set(self, key: str, value: str, description: str = "") -> None:
        """Set setting value."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a setting."""
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if setting exists."""
        ...

    @abstractmethod
    async def bulk_set(self, settings: Dict[str, str]) -> None:
        """Set multiple settings at once."""
        ...

    @abstractmethod
    async def get_typed(self, key: str, default: Any = None) -> Any:
        """Get setting with type coercion."""
        ...

    @abstractmethod
    async def initialize_defaults(self, defaults: Dict[str, str]) -> None:
        """Initialize default settings if not present."""
        ...
