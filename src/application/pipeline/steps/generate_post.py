"""Generate Post Step.

Selects template and generates post using LLM.
"""
from __future__ import annotations

import random
from typing import List

import structlog
from infrastructure.logging.logger import LoggingContext

from application.dto.pipeline_context import PipelineContext
from application.pipeline.step import PipelineStep
from application.services.llm_service import LLMService
from domain.value_objects.template import get_template, get_template_ids

logger = structlog.get_logger(__name__)


class GeneratePostStep(PipelineStep):
    """Generate post using template and LLM."""

    def __init__(
        self,
        llm_service: LLMService,
        min_length: int = 700,
        max_length: int = 730,
    ):
        self._llm_service = llm_service
        self._min_length = min_length
        self._max_length = max_length
        self._template_history: List[str] = []

    @property
    def name(self) -> str:
        return "generate_post"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        generated = []

        with LoggingContext(step="generate_post", total_articles=len(context.extracted_articles)):
            for extracted in context.extracted_articles:
                article_id = extracted.get("article_id")
                with LoggingContext(article_id=article_id):
                    try:
                        # Select template (with rotation)
                        template_id = self._select_template()
                        template = get_template(template_id)

                        if not template:
                            template = get_template("news_brief")
                            template_id = "news_brief"

                        # Prepare article data
                        article_data = {
                            "title": extracted.get("title", ""),
                            "summary": extracted.get("description", ""),
                            "content": extracted.get("content", ""),
                        }

                        # Generate post
                        logger.info("Generating post", article_id=article_id, template=template_id)
                        result = await self._llm_service.generate_post(
                            template_prompt=template.prompt,
                            article_data=article_data,
                            min_length=self._min_length,
                            max_length=self._max_length,
                        )

                        generated.append({
                            "article_id": extracted.get("article_id"),
                            "source_id": extracted.get("source_id"),
                            "template_id": template_id,
                            "post_text": result["post_text"],
                            "summary": result["summary"],
                            "image_url": extracted.get("image_url"),
                            "clean_url": extracted.get("url"),
                            "title": extracted.get("title", ""),
                        })

                        # Track template usage
                        self._template_history.append(template_id)
                        if len(self._template_history) > 10:
                            self._template_history.pop(0)

                        logger.info("Post generated", article_id=article_id, template=template_id)

                    except Exception as e:
                        logger.error("Post generation failed", article_id=article_id, error=str(e))
                        context.add_error(
                            self.name, f"Article {extracted.get('article_id')}: {e}")

        context.generated_posts = generated
        context.add_metric("generated_count", len(generated))
        logger.info("Post generation completed", total=len(generated))
        return context

    def _select_template(self) -> str:
        """Select template with rotation to avoid repetition."""
        available = get_template_ids()
        # Prefer templates not recently used
        unused = [t for t in available if t not in self._template_history]
        if unused:
            return random.choice(unused)
        return random.choice(available)
