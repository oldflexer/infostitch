"""Publish Step.

Publishes final posts to all enabled channels.
"""
from __future__ import annotations

from typing import List

import structlog
from infrastructure.logging.logger import LoggingContext

from application.dto.pipeline_context import PipelineContext
from application.pipeline.step import PipelineStep
from application.services.publisher_service import PublisherService
from domain.entities.post import Post

logger = structlog.get_logger(__name__)


class PublishStep(PipelineStep):
    """Publish posts to channels."""

    def __init__(self, publisher_service: PublisherService):
        self._publisher_service = publisher_service

    @property
    def name(self) -> str:
        return "publish"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        results = {}

        with LoggingContext(step="publish", total_posts=len(context.final_posts)):
            for post in context.final_posts:
                with LoggingContext(article_id=post.id, post_url=post.clean_url):
                    try:
                        # Prepare final text with source link and signature
                        final_text = self._format_post(post)

                        # Publish to all channels
                        logger.info("Publishing post", article_id=post.id, url=post.clean_url)
                        result = await self._publisher_service.publish_to_all(
                            text=final_text,
                            image_url=post.image_url,
                        )

                        results[post.clean_url] = result

                        # Mark post as published (in real implementation, save to DB)
                        # post.mark_published()

                        logger.info("Post published", article_id=post.id, channels=list(result.keys()))

                    except Exception as e:
                        logger.error("Post publishing failed", article_id=post.id, error=str(e))
                        context.add_error(self.name, f"Post {post.clean_url}: {e}")
                        results[post.clean_url] = {"error": str(e)}

        context.published_results = results
        context.add_metric("published_count", len(
            [r for r in results.values() if not r.get("error")]))
        logger.info("Publishing completed", total=len(results), successful=context.metrics.get("published_count", 0))
        return context

    def _format_post(self, post: Post) -> str:
        """Format post with source link and signature."""
        # Post content is already generated without link/signature
        # Add source link and channel signature
        source_link = f"\n\nИсточник: {post.clean_url}"
        signature = "\nПодготовлено каналом @myaiqnews"

        full_text = post.content + source_link + signature

        # Truncate to max length (1000 chars) with HTML tag repair
        max_length = 1000
        if len(full_text) > max_length:
            full_text = full_text[:max_length]
            # Repair unclosed HTML tags
            if "<b>" in full_text and "</b>" not in full_text:
                full_text += "</b>"

        return full_text
