"""Extract Content Step.

Extracts full article content and images using Jina AI.
"""
from __future__ import annotations

from typing import List

import structlog
from infrastructure.logging.logger import LoggingContext

from application.dto.pipeline_context import PipelineContext
from application.pipeline.step import PipelineStep
from application.services.image_service import ImageService
from domain.entities.article import Article

logger = structlog.get_logger(__name__)


class ExtractContentStep(PipelineStep):
    """Extract full content and images for selected articles."""

    def __init__(self, image_service: ImageService):
        self._image_service = image_service

    @property
    def name(self) -> str:
        return "extract_content"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        extracted = []

        with LoggingContext(step="extract_content", total_articles=len(context.selected_articles)):
            for article in context.selected_articles:
                with LoggingContext(article_id=article.id, article_url=str(article.url)):
                    try:
                        result = await self._image_service.extract_content_and_image(
                            str(article.url)
                        )
                        # Merge with original article data
                        result["article_id"] = article.id
                        result["source_id"] = article.source_id
                        result["original_title"] = article.title
                        result["published_at"] = article.published_at
                        extracted.append(result)
                        logger.info("Content extracted", article_id=article.id)
                    except Exception as e:
                        logger.error("Content extraction failed", article_id=article.id, error=str(e))
                        context.add_error(self.name, f"Article {article.id}: {e}")

        context.extracted_articles = extracted
        context.add_metric("extracted_count", len(extracted))
        logger.info("Content extraction completed", total=len(extracted))
        return context
