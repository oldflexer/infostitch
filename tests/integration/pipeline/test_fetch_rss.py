"""Integration tests for FetchRSSStep."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from application.dto.pipeline_context import PipelineContext
from domain.entities.rss_source import RssSource


class TestFetchRSSStep:
    """Tests for FetchRSSStep."""

    @pytest.fixture
    def sample_rss_sources(self):
        """Create sample RSS sources for testing."""
        return [
            RssSource(
                id=1,
                url="https://example.com/feed1.xml",
                enabled=True,
            ),
            RssSource(
                id=2,
                url="https://example.com/feed2.xml",
                enabled=True,
            ),
            RssSource(
                id=3,
                url="https://example.com/feed3.xml",
                enabled=False,  # Disabled source
            ),
        ]

    @pytest.fixture
    def mock_feedparser(self):
        """Mock feedparser to return test data."""
        with patch("application.pipeline.steps.fetch_rss.feedparser.parse") as mock:
            mock_feed = MagicMock()
            mock_feed.bozo = False
            # Use dict-like objects for entries (not MagicMock) so .get() works
            mock_feed.entries = [
                {
                    "title": "Test Article 1",
                    "link": "https://example.com/article1",
                    "summary": "Summary 1",
                    "published": "Mon, 01 Jan 2024 12:00:00 GMT",
                    "content": [{"value": "Full content 1"}],
                },
                {
                    "title": "Test Article 2",
                    "link": "https://example.com/article2",
                    "summary": "Summary 2",
                    "published": "Tue, 02 Jan 2024 12:00:00 GMT",
                    "content": [{"value": "Full content 2"}],
                },
            ]
            mock.return_value = mock_feed
            yield mock

    @pytest.mark.asyncio
    async def test_fetch_rss_success(
            self, fetch_rss_step, sample_rss_sources, mock_feedparser):
        """Test successful RSS fetching from multiple sources."""
        context = PipelineContext(rss_sources=sample_rss_sources)

        result = await fetch_rss_step.execute(context)

        assert result.raw_articles is not None
        assert len(result.raw_articles) == 4  # 2 articles per enabled source
        assert result.metrics["total_fetched"] == 4
        assert result.metrics["fetched_1"] == 2
        assert result.metrics["fetched_2"] == 2
        # Disabled source should not be fetched
        assert result.metrics.get("fetched_3") is None

    @pytest.mark.asyncio
    async def test_fetch_rss_disabled_source_skipped(
            self, fetch_rss_step, sample_rss_sources, mock_feedparser):
        """Test that disabled sources are skipped."""
        context = PipelineContext(rss_sources=sample_rss_sources)

        result = await fetch_rss_step.execute(context)

        # Only 2 enabled sources, 2 articles each = 4 total
        assert result.metrics["total_fetched"] == 4

    @pytest.mark.asyncio
    async def test_fetch_rss_handles_parse_error(
            self, fetch_rss_step, sample_rss_sources):
        """Test handling of feed parse errors."""
        with patch("application.pipeline.steps.fetch_rss.feedparser.parse") as mock_parse:
            mock_feed = MagicMock()
            mock_feed.bozo = True
            mock_feed.bozo_exception = Exception("Invalid XML")
            mock_parse.return_value = mock_feed

            context = PipelineContext(
                rss_sources=sample_rss_sources[:1])  # Only first source

            result = await fetch_rss_step.execute(context)

            # Should have error but continue
            assert len(result.errors) == 1
            assert "fetch_rss" in result.errors[0]
            assert "Invalid XML" in result.errors[0]
            assert result.raw_articles == []

    @pytest.mark.asyncio
    async def test_fetch_rss_handles_malformed_entries(
            self, fetch_rss_step, sample_rss_sources):
        """Test handling of malformed RSS entries."""
        with patch("application.pipeline.steps.fetch_rss.feedparser.parse") as mock_parse:
            mock_feed = MagicMock()
            mock_feed.bozo = False
            # One valid, one malformed entry
            mock_feed.entries = [
                {
                    "title": "Valid Article",
                    "link": "https://example.com/valid",
                    "summary": "Valid summary",
                    "published": "Mon, 01 Jan 2024 12:00:00 GMT",
                    "content": [{"value": "Valid content"}],
                },
                {
                    # Missing required fields - will cause exception in
                    # from_rss_entry
                    "title": None,
                    "link": None,
                },
            ]
            mock_parse.return_value = mock_feed

            context = PipelineContext(rss_sources=sample_rss_sources[:1])

            result = await fetch_rss_step.execute(context)

            # Should skip malformed entry, keep valid one
            assert len(result.raw_articles) == 1
            assert result.raw_articles[0].title == "Valid Article"

    @pytest.mark.asyncio
    async def test_fetch_rss_empty_feed(
            self, fetch_rss_step, sample_rss_sources):
        """Test handling of empty RSS feed."""
        with patch("application.pipeline.steps.fetch_rss.feedparser.parse") as mock_parse:
            mock_feed = MagicMock()
            mock_feed.bozo = False
            mock_feed.entries = []
            mock_parse.return_value = mock_feed

            context = PipelineContext(rss_sources=sample_rss_sources[:1])

            result = await fetch_rss_step.execute(context)

            assert result.raw_articles == []
            assert result.metrics["total_fetched"] == 0
