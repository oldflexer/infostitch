"""RssSource Entity.

Represents an RSS feed source configuration.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(slots=True)
class RssSource:
    """RSS source entity."""

    id: Optional[int] = None
    url: str = ""
    enabled: bool = True
    last_fetch: Optional[datetime] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate source after initialization."""
        if not self.url:
            raise ValueError("RSS source URL cannot be empty")
        if not self.url.startswith(("http://", "https://")):
            raise ValueError("RSS source URL must be HTTP/HTTPS")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "url": self.url,
            "enabled": self.enabled,
            "last_fetch": self.last_fetch.isoformat() if self.last_fetch else None,
            "created_at": self.created_at.isoformat(),
        }

    def mark_fetched(self) -> RssSource:
        """Return new source with updated last_fetch."""
        return RssSource(
            id=self.id,
            url=self.url,
            enabled=self.enabled,
            last_fetch=datetime.now(timezone.utc),
            created_at=self.created_at,
        )

    def toggle_enabled(self) -> RssSource:
        """Return new source with toggled enabled status."""
        return RssSource(
            id=self.id,
            url=self.url,
            enabled=not self.enabled,
            last_fetch=self.last_fetch,
            created_at=self.created_at,
        )
