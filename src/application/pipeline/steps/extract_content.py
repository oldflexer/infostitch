"""Extract Content Step.

Extracts full article content and images using Jina AI.
"""
from __future__ import annotations

from typing import List

from application.dto.pipeline_context import PipelineContext
from application.pipeline.step import PipelineStep
from application.services.image_service import ImageService
from domain.entities.article import Article


class ExtractContentStep(PipelineStep):
    """Extract full content and images for selected articles."""

    def __init__(self, image_service: ImageService):
        self._image_service = image_service

    @property
    def name(self) -> str:
        return "extract_content"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        extracted = []

        for article in context.selected_articles:
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
            except Exception as e:
                context.add_error(self.name, f"Article {article.id}: {e}")

        context.extracted_articles = extracted
        context.add_metric("extracted_count", len(extracted))
        return context
