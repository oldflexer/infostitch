"""Integration tests for DeduplicateStep."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from application.dto.pipeline_context import PipelineContext
from domain.entities.article import Article
from domain.value_objects.url import URL


class TestDeduplicateStep:
    """Tests for DeduplicateStep (Stage 1: URL + Jaccard)."""

    @pytest.fixture
    def sample_articles(self):
        """Create sample articles for testing."""
        return [
            Article(
                id=1,
                title="AI News: New Model Released",
                url=URL("https://example.com/article1"),
                summary="Summary 1",
                source_id=1,
            ),
            Article(
                id=2,
                title="AI News: New Model Released",
                url=URL("https://example.com/article2"),
                summary="Summary 2",
                source_id=1,
            ),
            Article(
                id=3,
                title="Different Topic: Quantum Computing",
                url=URL("https://example.com/article3"),
                summary="Summary 3",
                source_id=2,
            ),
            Article(
                id=4,
                title="AI News: New Model Released",
                url=URL("https://example.com/article1"),
                summary="Summary 4",
                source_id=3,
            ),
        ]

    @pytest.fixture
    def mock_dedup_service(self):
        """Create a mock deduplication service."""
        from application.services.deduplication_service import DeduplicationService
        from unittest.mock import MagicMock
        # Create a mock that doesn't require post_repo
        service = MagicMock(spec=DeduplicationService)
        service.filter_by_url = AsyncMock(side_effect=lambda articles: [
            a for i, a in enumerate(articles)
            if a.url not in [articles[j].url for j in range(i)]
        ])
        service.filter_by_jaccard = MagicMock(side_effect=lambda articles, recent_titles: [
            a for a in articles
            if a.title not in recent_titles
        ])
        return service

    @pytest.mark.asyncio
    async def test_deduplicate_url_stage(self, deduplicate_step, sample_articles, mock_dedup_service):
        """Test URL-based deduplication (Stage 1a)."""
        deduplicate_step._dedup_service = mock_dedup_service

        context = PipelineContext(raw_articles=sample_articles)

        result = await deduplicate_step.execute(context)

        assert len(result.deduplicated_articles) == 3
        assert result.metrics["after_url_dedup"] == 3

    @pytest.mark.asyncio
    async def test_deduplicate_jaccard_stage(self, deduplicate_step, sample_articles, mock_dedup_service):
        """Test Jaccard similarity deduplication (Stage 1b)."""
        deduplicate_step._dedup_service = mock_dedup_service

        context = PipelineContext(raw_articles=sample_articles[:3])
        # Mock get_recent_titles to return duplicate titles
        context.get_recent_titles = lambda limit=10: ["AI News: New Model Released"]

        result = await deduplicate_step.execute(context)

        # After URL dedup: 3 articles (articles 1, 2, 3)
        # After Jaccard: 1 article removed (articles 1 & 2 have same title as recent)
        assert len(result.deduplicated_articles) == 1
        assert result.metrics["after_jaccard_dedup"] == 1

    @pytest.mark.asyncio
    async def test_deduplicate_empty_input(self, deduplicate_step, mock_dedup_service):
        """Test deduplication with empty article list."""
        deduplicate_step._dedup_service = mock_dedup_service

        context = PipelineContext(raw_articles=[])

        result = await deduplicate_step.execute(context)

        assert result.deduplicated_articles == []
        assert result.metrics["after_url_dedup"] == 0
        assert result.metrics["after_jaccard_dedup"] == 0

    @pytest.mark.asyncio
    async def test_deduplicate_no_duplicates(self, deduplicate_step, mock_dedup_service):
        """Test deduplication when no duplicates exist."""
        deduplicate_step._dedup_service = mock_dedup_service

        unique_articles = [
            Article(
                id=1,
                title="Unique Title 1",
                url=URL("https://example.com/1"),
                summary="Summary 1",
                source_id=1,
            ),
            Article(
                id=2,
                title="Unique Title 2",
                url=URL("https://example.com/2"),
                summary="Summary 2",
                source_id=1,
            ),
        ]

        context = PipelineContext(raw_articles=unique_articles)
        context.get_recent_titles = lambda limit=10: []

        result = await deduplicate_step.execute(context)

        assert len(result.deduplicated_articles) == 2
        assert result.metrics["after_jaccard_dedup"] == 2

    @pytest.mark.asyncio
    async def test_deduplicate_all_duplicates(self, deduplicate_step, mock_dedup_service):
        """Test deduplication when all articles are duplicates."""
        deduplicate_step._dedup_service = mock_dedup_service

        duplicate_articles = [
            Article(
                id=1,
                title="Same Title",
                url=URL("https://example.com/1"),
                summary="Summary 1",
                source_id=1,
            ),
            Article(
                id=2,
                title="Same Title",
                url=URL("https://example.com/1"),
                summary="Summary 2",
                source_id=2,
            ),
        ]

        context = PipelineContext(raw_articles=duplicate_articles)
        context.get_recent_titles = lambda limit=10: ["Same Title"]

        result = await deduplicate_step.execute(context)

        assert len(result.deduplicated_articles) == 0
        assert result.metrics["after_jaccard_dedup"] == 0