"""User Entity.

Represents a dashboard user account.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(slots=True)
class User:
    """User entity for dashboard authentication."""

    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    role: str = "admin"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate user after initialization."""
        if not self.username:
            raise ValueError("Username cannot be empty")
        if not self.password_hash:
            raise ValueError("Password hash cannot be empty")
        if self.role not in ("admin", "viewer"):
            raise ValueError(f"Invalid role: {self.role}")

    def to_dict(self) -> dict:
        """Convert to dictionary (excludes password hash)."""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

    def update_last_login(self) -> User:
        """Return new user with updated last_login."""
        return User(
            id=self.id,
            username=self.username,
            password_hash=self.password_hash,
            role=self.role,
            created_at=self.created_at,
            last_login=datetime.now(timezone.utc),
        )