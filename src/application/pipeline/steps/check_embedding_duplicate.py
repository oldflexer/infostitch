"""Check Embedding Duplicate Step (Stage 2).

Semantic deduplication using embeddings.
"""
from __future__ import annotations

from typing import List

from application.dto.pipeline_context import PipelineContext
from application.pipeline.step import PipelineStep
from application.services.deduplication_service import DeduplicationService
from domain.entities.post import Post
from domain.value_objects.embedding import Embedding


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

        for i, (post_data, embedding) in enumerate(
            zip(context.generated_posts, context.post_embeddings)
        ):
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

            except Exception as e:
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
        return context
