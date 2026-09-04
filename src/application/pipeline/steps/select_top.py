"""Select Top Step.

Uses LLM to rank and select top articles.
"""
from __future__ import annotations

from typing import List

import structlog
from infrastructure.logging.logger import LoggingContext

from application.dto.pipeline_context import PipelineContext
from application.pipeline.step import PipelineStep
from application.services.llm_service import LLMService
from domain.entities.article import Article

logger = structlog.get_logger(__name__)


class SelectTopStep(PipelineStep):
    """Select top articles using LLM ranking."""

    def __init__(self, llm_service: LLMService, max_articles: int = 20):
        self._llm_service = llm_service
        self._max_articles = max_articles

    @property
    def name(self) -> str:
        return "select_top"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        articles = context.deduplicated_articles

        if not articles:
            context.selected_articles = []
            context.selected_article_indices = []
            context.add_metric("selected_count", 0)
            logger.info("No articles to select", total=0)
            return context

        with LoggingContext(step="select_top", total_candidates=len(articles)):
            try:
                # Prepare articles for LLM
                articles_for_llm = context.get_articles_for_selection()
                recent_titles = context.get_recent_titles(limit=10)

                # Get LLM ranking
                logger.info("Requesting LLM ranking", candidates=len(articles_for_llm))
                selected_indices = await self._llm_service.rank_articles(
                    articles=articles_for_llm,
                    recent_titles=context.get_recent_titles(limit=10),
                    max_count=self._max_articles,
                )

                # Limit to max_articles
                selected_indices = selected_indices[:self._max_articles]

                # Convert to 0-based indices and get selected articles
                selected_articles = []
                for idx in selected_indices:
                    if 1 <= idx <= len(articles):
                        selected_articles.append(articles[idx - 1])

                context.selected_article_indices = selected_indices
                context.selected_articles = selected_articles
                context.add_metric("selected_count", len(selected_articles))
                logger.info("Article selection completed",
                            selected=len(selected_articles), indices=selected_indices)

            except Exception as e:
                logger.error("LLM ranking failed", error=str(e))
                context.add_error(self.name, f"LLM ranking failed: {e}")
                context.selected_articles = []
                context.selected_article_indices = []

        return context
