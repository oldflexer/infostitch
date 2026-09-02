"""Integration tests for GeneratePostStep."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from application.dto.pipeline_context import PipelineContext


class TestGeneratePostStep:
    """Tests for GeneratePostStep (template + LLM post generation)."""

    @pytest.fixture
    def sample_extracted_articles(self):
        """Create sample extracted articles."""
        return [
            {
                "article_id": 1,
                "source_id": 1,
                "title": "AI Breakthrough",
                "summary": "Revolutionary AI model",
                "description": "Full content about AI...",
                "content": "Full article content...",
                "image_url": "https://example.com/image1.jpg",
                "url": "https://example.com/1",
            },
            {
                "article_id": 2,
                "source_id": 2,
                "title": "Quantum Computing",
                "summary": "Quantum milestone",
                "description": "Full content about quantum...",
                "content": "Full article content...",
                "image_url": None,
                "url": "https://example.com/2",
            },
        ]

    @pytest.fixture
    def mock_llm_service(self):
        """Create a mock LLM service."""
        from application.services.llm_service import LLMService
        service = MagicMock(spec=LLMService)
        service.generate_post = AsyncMock(side_effect=[
            {
                "post_text": "🚀 AI Breakthrough! Revolutionary model achieves human-level reasoning. #AI #Tech",
                "summary": "New AI model breakthrough",
            },
            {
                "post_text": "⚛️ Quantum Computing Milestone! Quantum computer solves impossible problem. #Quantum #Tech",
                "summary": "Quantum computing breakthrough",
            },
        ])
        return service

    @pytest.mark.asyncio
    async def test_generate_post_success(self, generate_post_step, sample_extracted_articles, mock_llm_service):
        """Test successful post generation."""
        generate_post_step._llm_service = mock_llm_service

        context = PipelineContext(extracted_articles=sample_extracted_articles)

        result = await generate_post_step.execute(context)

        assert len(result.generated_posts) == 2
        assert result.metrics["generated_count"] == 2

        # Check first post
        post1 = result.generated_posts[0]
        assert post1["article_id"] == 1
        assert post1["source_id"] == 1
        assert "AI Breakthrough" in post1["post_text"]
        assert post1["image_url"] == "https://example.com/image1.jpg"
        assert post1["clean_url"] == "https://example.com/1"

        # Check second post
        post2 = result.generated_posts[1]
        assert post2["article_id"] == 2
        assert post2["image_url"] is None

    @pytest.mark.asyncio
    async def test_generate_post_empty_input(self, generate_post_step, mock_llm_service):
        """Test generation with empty input."""
        generate_post_step._llm_service = mock_llm_service

        context = PipelineContext(extracted_articles=[])

        result = await generate_post_step.execute(context)

        assert result.generated_posts == []
        assert result.metrics["generated_count"] == 0
        mock_llm_service.generate_post.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_post_template_rotation(self, generate_post_step, sample_extracted_articles, mock_llm_service):
        """Test that template rotation works."""
        generate_post_step._llm_service = mock_llm_service

        context = PipelineContext(extracted_articles=sample_extracted_articles)

        result = await generate_post_step.execute(context)

        # Should have called generate_post twice with different templates
        assert mock_llm_service.generate_post.call_count == 2
        # Check that template_prompt was passed
        calls = mock_llm_service.generate_post.call_args_list
        assert len(calls) == 2
        # Both calls should have template_prompt
        for call in calls:
            assert "template_prompt" in call.kwargs

    @pytest.mark.asyncio
    async def test_generate_post_handles_errors(self, generate_post_step, sample_extracted_articles, mock_llm_service):
        """Test handling of generation errors."""
        generate_post_step._llm_service = mock_llm_service
        mock_llm_service.generate_post = AsyncMock(side_effect=[
            {"post_text": "Success", "summary": "Summary"},
            Exception("LLM rate limit"),
        ])

        context = PipelineContext(extracted_articles=sample_extracted_articles)

        result = await generate_post_step.execute(context)

        assert len(result.generated_posts) == 1
        assert len(result.errors) == 1
        assert "generate_post" in result.errors[0]
        assert "LLM rate limit" in result.errors[0]
        assert result.metrics["generated_count"] == 1

    @pytest.mark.asyncio
    async def test_generate_post_min_max_length(self, generate_post_step, sample_extracted_articles, mock_llm_service):
        """Test that min/max length parameters are passed."""
        generate_post_step._llm_service = mock_llm_service
        generate_post_step._min_length = 500
        generate_post_step._max_length = 1000

        context = PipelineContext(extracted_articles=sample_extracted_articles[:1])

        result = await generate_post_step.execute(context)

        call_args = mock_llm_service.generate_post.call_args
        assert call_args.kwargs["min_length"] == 500
        assert call_args.kwargs["max_length"] == 1000