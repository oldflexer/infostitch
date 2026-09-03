"""LLMModel Entity.

Represents an LLM provider configuration.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(slots=True)
class LLMModel:
    """LLM model entity."""

    id: Optional[int] = None
    name: str = ""
    provider: str = ""
    model_id: str = ""
    api_key_ref: str = ""
    is_active: bool = True
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate model after initialization."""
        if not self.name:
            raise ValueError("Model name cannot be empty")
        if not self.provider:
            raise ValueError("Provider cannot be empty")
        if not self.model_id:
            raise ValueError("Model ID cannot be empty")
        if not self.api_key_ref:
            raise ValueError("API key reference cannot be empty")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "model_id": self.model_id,
            "api_key_ref": self.api_key_ref,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }

    def toggle_active(self) -> LLMModel:
        """Return new model with toggled active status."""
        return LLMModel(
            id=self.id,
            name=self.name,
            provider=self.provider,
            model_id=self.model_id,
            api_key_ref=self.api_key_ref,
            is_active=not self.is_active,
            created_at=self.created_at,
        )
