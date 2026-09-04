"""Fetch RSS Step.

Fetches and normalizes RSS feeds from configured sources.
"""
from __future__ import annotations

import feedparser
from typing import List

import structlog
from infrastructure.logging.logger import LoggingContext, get_correlation_id

from application.dto.pipeline_context import PipelineContext
from application.pipeline.step import PipelineStep
from domain.entities.article import Article
from domain.entities.rss_source import RssSource
from domain.value_objects.url import URL

logger = structlog.get_logger(__name__)


class FetchRSSStep(PipelineStep):
    """Fetch RSS feeds and parse articles."""

    @property
    def name(self) -> str:
        return "fetch_rss"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        all_articles = []

        for source in context.rss_sources:
            if not source.enabled:
                continue

            # Add source context to logs
            with LoggingContext(source_id=source.id, source_url=str(source.url)):
                try:
                    articles = await self._fetch_source(source)
                    all_articles.extend(articles)
                    context.add_metric(f"fetched_{source.id}", len(articles))
                    logger.info("Source fetched", source_id=source.id, count=len(articles))
                except Exception as e:
                    logger.error("Source fetch failed", source_id=source.id, error=str(e))
                    context.add_error(self.name, f"Source {source.url}: {e}")

        context.raw_articles = all_articles
        context.add_metric("total_fetched", len(all_articles))
        logger.info("Fetch RSS completed", total_articles=len(all_articles))
        return context

    async def _fetch_source(self, source: RssSource) -> List[Article]:
        """Fetch and parse single RSS source."""
        feed = feedparser.parse(str(source.url))

        if feed.bozo and feed.bozo_exception:
            raise RuntimeError(f"Feed parse error: {feed.bozo_exception}")

        articles = []
        for entry in feed.entries:
            try:
                article = Article.from_rss_entry(entry, source.id)
                articles.append(article)
            except Exception:
                # Skip malformed entries
                continue

        return articles
