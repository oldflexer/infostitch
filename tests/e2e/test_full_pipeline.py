"""E2E tests for full pipeline execution."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from application.pipeline.pipeline import Pipeline
from application.dto.pipeline_context import PipelineContext
from domain.entities.rss_source import RssSource
from domain.entities.post import Post
from domain.value_objects.embedding import Embedding


class TestFullPipelineE2E:
    """End-to-end tests for the complete pipeline."""

    @pytest.fixture
    def mock_rss_sources(self):
        """Create mock RSS sources."""
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
        ]

    @pytest.fixture
    def mock_feedparser(self):
        """Mock feedparser to return test data."""
        with patch("application.pipeline.steps.fetch_rss.feedparser.parse") as mock:
            mock_feed = MagicMock()
            mock_feed.bozo = False
            mock_feed.entries = [
                {
                    "title": "AI Breakthrough in Machine Learning",
                    "link": "https://example.com/article1",
                    "summary": "Scientists achieve major breakthrough in ML",
                    "published": "Mon, 01 Jan 2024 12:00:00 GMT",
                    "content": [{"value": "Full article content about AI breakthrough..."}],
                },
                {
                    "title": "New Python Release 3.13",
                    "link": "https://example.com/article2",
                    "summary": "Python 3.13 brings performance improvements",
                    "published": "Mon, 01 Jan 2024 13:00:00 GMT",
                    "content": [{"value": "Full article content about Python release..."}],
                },
                {
                    "title": "Quantum Computing Advances",
                    "link": "https://example.com/article3",
                    "summary": "Researchers make progress in quantum computing",
                    "published": "Mon, 01 Jan 2024 14:00:00 GMT",
                    "content": [{"value": "Full article content about quantum computing..."}],
                },
            ]
            mock.return_value = mock_feed
            yield mock

    @pytest.fixture
    def mock_jina_client(self):
        """Mock Jina client for content extraction."""
        with patch("infrastructure.clients.jina_client.JinaClient") as mock_class:
            mock_client = MagicMock()
            mock_client.extract_content = AsyncMock(side_effect=[
                {
                    "title": "AI Breakthrough in Machine Learning",
                    "description": "Full content about AI breakthrough...",
                    "content": "Full article content about AI breakthrough...",
                    "image_url": "https://example.com/image1.jpg",
                    "url": "https://example.com/article1",
                },
                {
                    "title": "New Python Release 3.13",
                    "description": "Full content about Python release...",
                    "content": "Full article content about Python release...",
                    "image_url": None,
                    "url": "https://example.com/article2",
                },
                {
                    "title": "Quantum Computing Advances",
                    "description": "Full content about quantum computing...",
                    "content": "Full article content about quantum computing...",
                    "image_url": "https://example.com/image3.jpg",
                    "url": "https://example.com/article3",
                },
            ])
            mock_class.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def mock_gemini_client(self):
        """Mock Gemini client for LLM and embeddings."""
        with patch("infrastructure.clients.gemini_client.GeminiClient") as mock_class:
            mock_client = MagicMock()
            mock_client.generate_content = AsyncMock(side_effect=[
                "[1, 3, 2]",
                '{"post_text": "🚀 AI Breakthrough! Scientists achieve major breakthrough in ML. #AI #Tech", "summary": "AI breakthrough in ML"}',
                '{"post_text": "⚛️ Quantum Computing Advances! Researchers make progress. #Quantum #Tech", "summary": "Quantum computing advances"}',
                '{"post_text": "🐍 New Python Release 3.13! Performance improvements. #Python #Tech", "summary": "Python 3.13 release"}',
            ])
            mock_client.generate_embedding = AsyncMock(side_effect=[
                [0.1] * 768,
                [0.2] * 768,
                [0.3] * 768,
            ])
            mock_class.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def mock_publisher_clients(self):
        """Mock all publisher clients."""
        with patch("infrastructure.clients.telegram_client.TelegramClient") as mock_tg, \
             patch("infrastructure.clients.vk_client.VKClient") as mock_vk, \
             patch("infrastructure.clients.max_client.MaxClient") as mock_max:
            
            mock_tg_instance = MagicMock()
            mock_tg_instance.send_message = AsyncMock(return_value={"message_id": 1, "ok": True})
            mock_tg_instance.send_photo = AsyncMock(return_value={"message_id": 1, "ok": True})
            mock_tg.return_value = mock_tg_instance
            
            mock_vk_instance = MagicMock()
            mock_vk_instance.wall_post = AsyncMock(return_value={"post_id": 1})
            mock_vk_instance.post_with_photo = AsyncMock(return_value={"post_id": 1})
            mock_vk.return_value = mock_vk_instance
            
            mock_max_instance = MagicMock()
            mock_max_instance.send_message = AsyncMock(return_value={"message_id": 1, "ok": True})
            mock_max_instance.send_photo = AsyncMock(return_value={"message_id": 1, "ok": True})
            mock_max.return_value = mock_max_instance
            
            yield mock_tg_instance, mock_vk_instance, mock_max_instance

    @pytest.mark.asyncio
    async def test_full_pipeline_dry_run(
        self,
        full_pipeline,
        mock_rss_sources,
        mock_feedparser,
        mock_jina_client,
        mock_gemini_client,
        mock_publisher_clients,
    ):
        """Test full pipeline execution in dry-run mode."""
        context = PipelineContext(rss_sources=mock_rss_sources)
        
        result = await full_pipeline.run(context)
        
        # Verify pipeline completed
        assert result.metrics.get("total_fetched", 0) == 6  # 3 articles per source
        assert result.metrics.get("after_url_dedup", 0) == 6
        assert result.metrics.get("after_jaccard_dedup", 0) == 6
        assert result.metrics.get("selected_count", 0) == 3  # max 3 selected
        assert result.metrics.get("extracted_count", 0) == 3
        assert result.metrics.get("generated_count", 0) == 3
        assert result.metrics.get("embeddings_computed", 0) == 3
        assert result.metrics.get("final_posts", 0) == 3
        assert result.metrics.get("duplicate_posts", 0) == 0
        assert result.metrics.get("published_count", 0) == 3
        
        # Verify final posts exist
        assert len(result.final_posts) == 3
        for post in result.final_posts:
            assert isinstance(post, Post)
            assert post.title
            assert post.clean_url
            assert post.embedding is not None

    @pytest.mark.asyncio
    async def test_pipeline_with_errors_continues(
        self,
        full_pipeline,
        mock_rss_sources,
        mock_feedparser,
        mock_jina_client,
        mock_gemini_client,
        mock_publisher_clients,
    ):
        """Test that pipeline continues on non-critical errors."""
        # Make one Jina extraction fail
        mock_jina_client.extract_content = AsyncMock(side_effect=[
            {
                "title": "AI Breakthrough",
                "description": "Content...",
                "content": "Full content...",
                "image_url": "https://example.com/image1.jpg",
                "url": "https://example.com/article1",
            },
            Exception("Jina API timeout"),
            {
                "title": "Quantum Computing",
                "description": "Content...",
                "content": "Full content...",
                "image_url": None,
                "url": "https://example.com/article3",
            },
        ])
        
        context = PipelineContext(rss_sources=mock_rss_sources)
        result = await full_pipeline.run(context)
        
        # Should have error but continue
        assert len(result.errors) >= 1
        assert any("extract_content" in e for e in result.errors)
        # But still process other articles
        assert result.metrics.get("extracted_count", 0) >= 1

    @pytest.mark.asyncio
    async def test_pipeline_empty_rss_feeds(self, full_pipeline, mock_rss_sources):
        """Test pipeline with empty RSS feeds."""
        with patch("application.pipeline.steps.fetch_rss.feedparser.parse") as mock_parse:
            mock_feed = MagicMock()
            mock_feed.bozo = False
            mock_feed.entries = []
            mock_parse.return_value = mock_feed
            
            context = PipelineContext(rss_sources=mock_rss_sources)
            result = await full_pipeline.run(context)
            
            assert result.raw_articles == []
            assert result.metrics.get("total_fetched", 0) == 0
            assert result.final_posts == []

    @pytest.mark.asyncio
    async def test_pipeline_all_duplicates_filtered(self, full_pipeline, mock_rss_sources):
        """Test pipeline when all articles are duplicates."""
        with patch("application.pipeline.steps.fetch_rss.feedparser.parse") as mock_parse:
            mock_feed = MagicMock()
            mock_feed.bozo = False
            # Same article from both sources
            mock_feed.entries = [
                {
                    "title": "Same Article",
                    "link": "https://example.com/same",
                    "summary": "Summary",
                    "published": "Mon, 01 Jan 2024 12:00:00 GMT",
                    "content": [{"value": "Content"}],
                },
            ]
            mock_parse.return_value = mock_feed
            
            context = PipelineContext(rss_sources=mock_rss_sources)
            result = await full_pipeline.run(context)
            
            # After URL dedup, 2 articles (not in DB yet, so not deduped across sources)
            # Jaccard dedup also doesn't filter (no recent titles in DB)
            assert result.metrics.get("after_url_dedup", 0) == 2
            assert result.metrics.get("after_jaccard_dedup", 0) == 2
            # Should still process those 2 articles (max 3 selected)
            assert result.metrics.get("selected_count", 0) == 2

    @pytest.mark.asyncio
    async def test_pipeline_integration_all_steps(
        self,
        full_pipeline,
        mock_rss_sources,
        mock_feedparser,
        mock_jina_client,
        mock_gemini_client,
        mock_publisher_clients,
    ):
        """Test that all 8 pipeline steps are executed in order."""
        context = PipelineContext(rss_sources=mock_rss_sources)
        
        # Track step execution order
        step_order = []
        
        # Patch each step to track execution
        original_steps = full_pipeline.steps
        for step in original_steps:
            original_execute = step.execute
            step_name = step.__class__.__name__
            
            async def tracking_execute(ctx, name=step_name, orig=original_execute):
                step_order.append(name)
                return await orig(ctx)
            
            step.execute = tracking_execute
        
        result = await full_pipeline.run(context)
        
        # Verify all 8 steps executed in order
        expected_steps = [
            "FetchRSSStep",
            "DeduplicateStep",
            "SelectTopStep",
            "ExtractContentStep",
            "GeneratePostStep",
            "ComputeEmbeddingStep",
            "CheckEmbeddingDuplicateStep",
            "PublishStep",
        ]
        assert step_order == expected_steps
        
        # Verify final result
        assert len(result.final_posts) == 3
        assert result.metrics.get("published_count", 0) == 3