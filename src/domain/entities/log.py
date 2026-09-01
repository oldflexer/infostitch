"""Log Entity.

Represents a structured application log entry.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass(slots=True)
class Log:
    """Structured application log entry."""

    id: Optional[int] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now())
    level: str = "INFO"
    module: str = ""
    message: str = ""
    context_json: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate log after initialization."""
        if not self.level:
            raise ValueError("Log level cannot be empty")
        if not self.module:
            raise ValueError("Log module cannot be empty")
        if not self.message:
            raise ValueError("Log message cannot be empty")

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "level": self.level,
            "module": self.module,
            "message": self.message,
            "context_json": self.context_json,
            "user_id": self.user_id,
        }

    @classmethod
    def create(
        cls,
        level: str,
        module: str,
        message: str,
        context_json: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
    ) -> "Log":
        """Factory method to create a new log entry."""
        return cls(
            level=level,
            module=module,
            message=message,
            context_json=context_json,
            user_id=user_id,
        )