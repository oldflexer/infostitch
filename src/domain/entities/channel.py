"""Channel Entity.

Represents a publishing channel (Telegram, VK, Max).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass(slots=True)
class Channel:
    """Publishing channel entity."""

    id: Optional[int] = None
    name: str = ""
    type: str = ""  # telegram, vk, max
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate channel after initialization."""
        if not self.name:
            raise ValueError("Channel name cannot be empty")
        if self.type not in ("telegram", "vk", "max"):
            raise ValueError(f"Invalid channel type: {self.type}")

        # Validate config based on type
        required_keys = {
            "telegram": ["chat_id", "bot_token_ref"],
            "vk": ["group_id", "access_token_ref"],
            "max": ["chat_id", "bot_token_ref"],
        }
        for key in required_keys.get(self.type, []):
            if key not in self.config:
                raise ValueError(
                    f"Missing required config key for {self.type}: {key}")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "enabled": self.enabled,
            "config": self.config,
            "created_at": self.created_at.isoformat(),
        }

    def toggle_enabled(self) -> Channel:
        """Return new channel with toggled enabled status."""
        return Channel(
            id=self.id,
            name=self.name,
            type=self.type,
            enabled=not self.enabled,
            config=self.config,
            created_at=self.created_at,
        )

    def update_config(self, config: Dict[str, Any]) -> Channel:
        """Return new channel with updated config."""
        return Channel(
            id=self.id,
            name=self.name,
            type=self.type,
            enabled=self.enabled,
            config=config,
            created_at=self.created_at,
        )

    @property
    def chat_id(self) -> Optional[str]:
        """Get chat_id from config."""
        return self.config.get("chat_id") or self.config.get("group_id")

    @property
    def token_ref(self) -> Optional[str]:
        """Get token reference from config."""
        return (
            self.config.get("bot_token_ref")
            or self.config.get("access_token_ref")
        )
