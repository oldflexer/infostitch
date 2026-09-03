"""LLM Model Repository Interface.

Defines the contract for LLM model data access.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.llm_model import LLMModel


class LLMModelRepository(ABC):
    """Abstract repository for LLMModel entities."""

    @abstractmethod
    async def add(self, model: LLMModel) -> LLMModel:
        """Add a new LLM model."""
        ...

    @abstractmethod
    async def get_by_id(self, model_id: int) -> Optional[LLMModel]:
        """Get model by ID."""
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[LLMModel]:
        """Get model by name."""
        ...

    @abstractmethod
    async def get_all(self, active_only: bool = False) -> List[LLMModel]:
        """Get all models."""
        ...

    @abstractmethod
    async def get_active(self) -> List[LLMModel]:
        """Get only active models."""
        ...

    @abstractmethod
    async def get_by_provider(self, provider: str) -> List[LLMModel]:
        """Get models by provider."""
        ...

    @abstractmethod
    async def update(self, model: LLMModel) -> LLMModel:
        """Update an existing model."""
        ...

    @abstractmethod
    async def delete(self, model_id: int) -> bool:
        """Delete a model."""
        ...

    @abstractmethod
    async def count(self) -> int:
        """Count total models."""
        ...
