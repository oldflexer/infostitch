"""Deduplicate Step (Stage 1).

Filters articles by URL and Jaccard similarity.
"""
from __future__ import annotations

from typing import List

import structlog
from infrastructure.logging.logger import LoggingContext

from application.dto.pipeline_context import PipelineContext
from application.pipeline.step import PipelineStep
from application.services.deduplication_service import DeduplicationService
from domain.entities.article import Article

logger = structlog.get_logger(__name__)


class DeduplicateStep(PipelineStep):
    """Deduplicate articles (Stage 1: URL + Jaccard)."""

    def __init__(self, dedup_service: DeduplicationService):
        self._dedup_service = dedup_service

    @property
    def name(self) -> str:
        return "deduplicate_stage1"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        articles = context.raw_articles

        with LoggingContext(step="deduplicate_stage1"):
            # Stage 1a: URL deduplication
            original_count = len(articles)
            articles = await self._dedup_service.filter_by_url(articles)
            url_dedup_count = original_count - len(articles)
            context.add_metric("after_url_dedup", len(articles))
            logger.info("URL deduplication completed",
                        original=original_count, removed=url_dedup_count, remaining=len(articles))

            # Stage 1b: Jaccard similarity deduplication
            # Get recent titles from context or repo
            recent_titles = context.get_recent_titles(limit=20)
            original_count = len(articles)
            articles = self._dedup_service.filter_by_jaccard(
                articles, recent_titles)
            jaccard_dedup_count = original_count - len(articles)
            context.add_metric("after_jaccard_dedup", len(articles))
            logger.info("Jaccard deduplication completed",
                        original=original_count, removed=jaccard_dedup_count, remaining=len(articles))

        context.deduplicated_articles = articles
        return context
