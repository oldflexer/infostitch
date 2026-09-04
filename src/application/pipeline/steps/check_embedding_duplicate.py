"""Check Embedding Duplicate Step (Stage 2).

Semantic deduplication using embeddings.
"""
from __future__ import annotations

from typing import List

import structlog
from infrastructure.logging.logger import LoggingContext

from application.dto.pipeline_context import PipelineContext
from application.pipeline.step import PipelineStep
from application.services.deduplication_service import DeduplicationService
from domain.entities.post import Post
from domain.value_objects.embedding import Embedding

logger = structlog.get_logger(__name__)


class CheckEmbeddingDuplicateStep(PipelineStep):
    """Check semantic duplicates using embeddings (Stage 2)."""

    def __init__(self, dedup_service: DeduplicationService):
        self._dedup_service = dedup_service

    @property
    def name(self) -> str:
        return "check_embedding_duplicate"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        final_posts = []
        duplicate_posts = []

        with LoggingContext(step="check_embedding_duplicate", total_posts=len(context.generated_posts)):
            for i, (post_data, embedding) in enumerate(
                zip(context.generated_posts, context.post_embeddings)
            ):
                article_id = post_data.get("article_id")
                with LoggingContext(article_id=article_id):
                    try:
                        # Check semantic duplicate
                        duplicate = await self._dedup_service.is_duplicate_by_embedding(embedding)

                        if duplicate:
                            # Mark as duplicate
                            post = Post(
                                title=post_data["title"],
                                summary=post_data["summary"],
                                content=post_data["post_text"],
                                clean_url=post_data["clean_url"],
                                embedding=embedding,
                                image_url=post_data.get("image_url"),
                                is_duplicate=True,
                                source_id=post_data.get("source_id"),
                                template_id=post_data.get("template_id"),
                            )
                            duplicate_posts.append(post)
                            logger.info("Semantic duplicate detected", article_id=article_id, matched_post=duplicate.get("post_id"))
                        else:
                            # Create final post
                            post = Post(
                                title=post_data["title"],
                                summary=post_data["summary"],
                                content=post_data["post_text"],
                                clean_url=post_data["clean_url"],
                                embedding=embedding,
                                image_url=post_data.get("image_url"),
                                is_duplicate=False,
                                source_id=post_data.get("source_id"),
                                template_id=post_data.get("template_id"),
                            )
                            final_posts.append(post)
                            logger.info("Post passed semantic check", article_id=article_id)

                    except Exception as e:
                        logger.error("Embedding duplicate check failed", article_id=article_id, error=str(e))
                        context.add_error(
                            self.name, f"Post {post_data.get('clean_url', i)}: {e}")
                        # On error, treat as non-duplicate to continue pipeline
                        post = Post(
                            title=post_data["title"],
                            summary=post_data["summary"],
                            content=post_data["post_text"],
                            clean_url=post_data["clean_url"],
                            embedding=embedding,
                            image_url=post_data.get("image_url"),
                            is_duplicate=False,
                            source_id=post_data.get("source_id"),
                            template_id=post_data.get("template_id"),
                        )
                        final_posts.append(post)

        context.final_posts = final_posts
        context.duplicate_posts = duplicate_posts
        context.add_metric("final_posts", len(final_posts))
        context.add_metric("duplicate_posts", len(duplicate_posts))
        logger.info("Embedding duplicate check completed", final=len(final_posts), duplicates=len(duplicate_posts))
        return context
