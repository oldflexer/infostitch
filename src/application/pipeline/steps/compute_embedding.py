"""Compute Embedding Step.

Generates embeddings for generated posts.
"""
from __future__ import annotations

from typing import List

from application.dto.pipeline_context import PipelineContext
from application.pipeline.step import PipelineStep
from application.services.embedding_service import EmbeddingService
from domain.value_objects.embedding import Embedding


class ComputeEmbeddingStep(PipelineStep):
    """Compute embeddings for posts."""

    def __init__(self, embedding_service: EmbeddingService):
        self._embedding_service = embedding_service

    @property
    def name(self) -> str:
        return "compute_embedding"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        embeddings = []

        for post in context.generated_posts:
            try:
                # Create text for embedding: title + summary
                text = f"{post['title']}. {post['summary']}"

                embedding = await self._embedding_service.generate_embedding(text)
                embeddings.append(Embedding.from_list(embedding))
            except Exception as e:
                context.add_error(
                    self.name, f"Post {post.get('article_id')}: {e}")
                # Add zero embedding as fallback
                embeddings.append(Embedding.from_list([0.0] * 768))

        context.post_embeddings = embeddings
        context.add_metric("embeddings_computed", len(embeddings))
        return context
