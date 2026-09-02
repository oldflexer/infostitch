"""Unit tests for LLMModel entity."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from domain.entities.llm_model import LLMModel


class TestLLMModel:
    """Tests for LLMModel entity."""

    def test_create_llm_model(self):
        """Test creating an LLM model."""
        model = LLMModel(
            id=1,
            name="gemini-1.5-flash",
            provider="gemini",
            model_id="gemini-1.5-flash-latest",
            api_key_ref="GEMINI_API_KEY",
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        
        assert model.id == 1
        assert model.name == "gemini-1.5-flash"
        assert model.provider == "gemini"
        assert model.model_id == "gemini-1.5-flash-latest"
        assert model.api_key_ref == "GEMINI_API_KEY"
        assert model.is_active is True