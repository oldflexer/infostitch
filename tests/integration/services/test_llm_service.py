"""Integration tests for LLMService."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from application.services.llm_service import LLMService, MockLLMProvider


class TestLLMService:
    """Tests for LLMService."""

    @pytest.fixture
    def llm_service(self):
        """Create LLMService with mock provider."""
        return LLMService(provider=MockLLMProvider())

    @pytest.mark.asyncio
    async def test_generate_text(self, llm_service):
        """Test basic text generation."""
        result = await llm_service.generate(
            prompt="Write a short sentence about AI.",
            temperature=0.7,
            max_tokens=100,
        )
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_generate_json(self, llm_service):
        """Test JSON response format."""
        result = await llm_service.generate(
            prompt="Return JSON with key 'test' and value 'value'.",
            response_format="json",
            temperature=0.3,
            max_tokens=100,
        )
        import json
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    @pytest.mark.asyncio
    async def test_rank_articles(self, llm_service):
        """Test article ranking."""
        articles = [
            {"id": 1, "title": "AI Breakthrough", "summary": "Revolutionary AI model"},
            {"id": 2, "title": "Python Release", "summary": "Python 3.13 released"},
            {"id": 3, "title": "Quantum Computing", "summary": "Quantum milestone"},
        ]
        recent_titles = ["Old Article"]

        result = await llm_service.rank_articles(
            articles=articles,
            recent_titles=recent_titles,
            max_count=2,
        )

        assert isinstance(result, list)
        assert len(result) <= 2
        assert all(isinstance(i, int) for i in result)
        assert all(1 <= i <= len(articles) for i in result)

    @pytest.mark.asyncio
    async def test_rank_articles_empty(self, llm_service):
        """Test ranking with empty article list."""
        result = await llm_service.rank_articles(
            articles=[],
            recent_titles=[],
            max_count=5,
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_generate_post(self, llm_service):
        """Test post generation from template."""
        template_prompt = "Write a post about {title}. Summary: {summary}. Min: {min_length}, Max: {max_length}"
        article_data = {
            "title": "AI Breakthrough",
            "summary": "Revolutionary AI model achieves human-level reasoning",
            "content": "Full article content here...",
        }

        result = await llm_service.generate_post(
            template_prompt=template_prompt,
            article_data=article_data,
            min_length=100,
            max_length=200,
        )

        assert "post_text" in result
        assert "summary" in result
        assert isinstance(result["post_text"], str)
        assert isinstance(result["summary"], str)
        assert len(result["post_text"]) > 0

    @pytest.mark.asyncio
    async def test_call_count_tracking(self, llm_service):
        """Test that call count is tracked in mock provider."""
        provider = llm_service.provider
        initial_count = provider.call_count

        await llm_service.generate(prompt="Test 1")
        await llm_service.generate(prompt="Test 2")

        assert provider.call_count == initial_count + 2