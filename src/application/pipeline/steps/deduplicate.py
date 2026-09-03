"""Deduplicate Step (Stage 1).

Filters articles by URL and Jaccard similarity.
"""
from __future__ import annotations

from typing import List

from application.dto.pipeline_context import PipelineContext
from application.pipeline.step import PipelineStep
from application.services.deduplication_service import DeduplicationService
from domain.entities.article import Article


class DeduplicateStep(PipelineStep):
    """Deduplicate articles (Stage 1: URL + Jaccard)."""

    def __init__(self, dedup_service: DeduplicationService):
        self._dedup_service = dedup_service

    @property
    def name(self) -> str:
        return "deduplicate_stage1"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        articles = context.raw_articles

        # Stage 1a: URL deduplication
        articles = await self._dedup_service.filter_by_url(articles)
        context.add_metric("after_url_dedup", len(articles))

        # Stage 1b: Jaccard similarity deduplication
        # Get recent titles from context or repo
        recent_titles = context.get_recent_titles(limit=20)
        articles = self._dedup_service.filter_by_jaccard(
            articles, recent_titles)
        context.add_metric("after_jaccard_dedup", len(articles))

        context.deduplicated_articles = articles
        return context
