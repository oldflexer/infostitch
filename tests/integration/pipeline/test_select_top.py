"""Integration tests for SelectTopStep."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from application.dto.pipeline_context import PipelineContext
from domain.entities.article import Article
from domain.value_objects.url import URL


class TestSelectTopStep:
    """Tests for SelectTopStep (LLM-based article ranking)."""

    @pytest.fixture
    def sample_articles(self):
        """Create sample articles for testing."""
        return [
            Article(
                id=1,
                title="Breaking: Major AI Breakthrough",
                url=URL("https://example.com/1"),
                summary="Revolutionary AI model achieves human-level reasoning",
                source_id=1,
            ),
            Article(
                id=2,
                title="New Python Release",
                url=URL("https://example.com/2"),
                summary="Python 3.13 brings performance improvements",
                source_id=1,
            ),
            Article(
                id=3,
                title="Quantum Computing Milestone",
                url=URL("https://example.com/3"),
                summary="Quantum computer solves previously impossible problem",
                source_id=2,
            ),
            Article(
                id=4,
                title="Tech Company Earnings",
                url=URL("https://example.com/4"),
                summary="Quarterly results exceed expectations",
                source_id=3,
            ),
        ]

    @pytest.fixture
    def mock_llm_service(self):
        """Create a mock LLM service."""
        from application.services.llm_service import LLMService
        service = MagicMock(spec=LLMService)
        # Mock rank_articles to return indices (1-based)
        service.rank_articles = AsyncMock(return_value=[1, 3, 2])  # Select articles 1, 3, 2
        return service

    @pytest.mark.asyncio
    async def test_select_top_success(self, select_top_step, sample_articles, mock_llm_service):
        """Test successful article selection."""
        select_top_step._llm_service = mock_llm_service

        context = PipelineContext(deduplicated_articles=sample_articles)

        result = await select_top_step.execute(context)

        assert len(result.selected_articles) == 3
        assert result.selected_article_indices == [1, 3, 2]
        assert result.metrics["selected_count"] == 3
        # Verify selected articles match indices (1-based)
        assert result.selected_articles[0].id == 1
        assert result.selected_articles[1].id == 3
        assert result.selected_articles[2].id == 2

    @pytest.mark.asyncio
    async def test_select_top_empty_input(self, select_top_step, mock_llm_service):
        """Test selection with empty article list."""
        select_top_step._llm_service = mock_llm_service

        context = PipelineContext(deduplicated_articles=[])

        result = await select_top_step.execute(context)

        assert result.selected_articles == []
        assert result.selected_article_indices == []
        assert result.metrics["selected_count"] == 0
        # LLM should not be called
        mock_llm_service.rank_articles.assert_not_called()

    @pytest.mark.asyncio
    async def test_select_top_max_articles_limit(self, select_top_step, sample_articles, mock_llm_service):
        """Test that max_articles limit is respected."""
        select_top_step._llm_service = mock_llm_service
        select_top_step._max_articles = 2

        context = PipelineContext(deduplicated_articles=sample_articles)

        result = await select_top_step.execute(context)

        # Should only select up to max_articles
        assert len(result.selected_articles) == 2
        assert result.metrics["selected_count"] == 2

    @pytest.mark.asyncio
    async def test_select_top_invalid_indices_handled(self, select_top_step, sample_articles, mock_llm_service):
        """Test handling of invalid indices from LLM."""
        select_top_step._llm_service = mock_llm_service
        # Return invalid indices (out of range)
        mock_llm_service.rank_articles = AsyncMock(return_value=[1, 5, 10, -1])

        context = PipelineContext(deduplicated_articles=sample_articles)

        result = await select_top_step.execute(context)

        # Should only include valid indices (1-4)
        assert len(result.selected_articles) == 1
        assert result.selected_articles[0].id == 1

    @pytest.mark.asyncio
    async def test_select_top_llm_error_handled(self, select_top_step, sample_articles, mock_llm_service):
        """Test handling of LLM service errors."""
        select_top_step._llm_service = mock_llm_service
        mock_llm_service.rank_articles = AsyncMock(side_effect=Exception("LLM API error"))

        context = PipelineContext(deduplicated_articles=sample_articles)

        result = await select_top_step.execute(context)

        # Should have error but not crash
        assert len(result.errors) == 1
        assert "select_top" in result.errors[0]
        assert "LLM API error" in result.errors[0]
        assert result.selected_articles == []