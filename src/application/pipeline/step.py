"""Pipeline Step Base Class.

Abstract base class for pipeline steps.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from application.dto.pipeline_context import PipelineContext


class PipelineStep(ABC):
    """Abstract pipeline step."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Step name for logging."""
        ...

    @abstractmethod
    async def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute step and return updated context."""
        ...