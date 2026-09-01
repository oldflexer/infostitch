"""Embedding Service.

Provides embedding generation using LLM provider.
"""
from __future__ import annotations

from typing import List, Optional

from infrastructure.clients.gemini_client import GeminiClient, MockGeminiClient
from infrastructure.config import get_settings


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self, client: Optional[GeminiClient] = None):
        self._client = client or self._create_default_client()

    def _create_default_client(self) -> GeminiClient:
        settings = get_settings()
        if settings.app_env == "development" and not settings.gemini_api_key:
            return MockGeminiClient()
        return GeminiClient()

    async def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> List[float]:
        """Generate embedding for single text."""
        settings = get_settings()
        model = model or settings.embedding_model
        return await self._client.generate_embedding(
            text=text,
            model=model,
            task_type=task_type,
        )

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        model: Optional[str] = None,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        settings = get_settings()
        model = model or settings.embedding_model
        return await self._client.generate_embeddings_batch(
            texts=texts,
            model=model,
            task_type=task_type,
        )

    async def close(self) -> None:
        await self._client.close()