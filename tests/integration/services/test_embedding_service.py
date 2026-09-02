"""Integration tests for EmbeddingService."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from application.services.embedding_service import EmbeddingService


class TestEmbeddingService:
    """Tests for EmbeddingService."""

    @pytest.fixture
    def mock_gemini_client(self):
        """Create a mock Gemini client."""
        from infrastructure.clients.gemini_client import MockGeminiClient
        return MockGeminiClient()

    @pytest.fixture
    def embedding_service(self, mock_gemini_client):
        """Create EmbeddingService with mock client."""
        return EmbeddingService(client=mock_gemini_client)

    @pytest.mark.asyncio
    async def test_generate_embedding(self, embedding_service):
        """Test single embedding generation."""
        text = "Test article about AI breakthrough"
        result = await embedding_service.generate_embedding(text)

        assert isinstance(result, list)
        assert len(result) == 768
        assert all(isinstance(v, float) for v in result)

    @pytest.mark.asyncio
    async def test_generate_embedding_with_model(self, embedding_service):
        """Test embedding generation with specific model."""
        text = "Test text"
        result = await embedding_service.generate_embedding(
            text=text,
            model="text-embedding-004",
            task_type="RETRIEVAL_DOCUMENT",
        )

        assert isinstance(result, list)
        assert len(result) == 768

    @pytest.mark.asyncio
    async def test_generate_embeddings_batch(self, embedding_service):
        """Test batch embedding generation."""
        texts = [
            "First article about AI",
            "Second article about Python",
            "Third article about Quantum",
        ]

        result = await embedding_service.generate_embeddings_batch(texts)

        assert isinstance(result, list)
        assert len(result) == 3
        assert all(len(emb) == 768 for emb in result)

    @pytest.mark.asyncio
    async def test_generate_embeddings_batch_empty(self, embedding_service):
        """Test batch embedding with empty list."""
        result = await embedding_service.generate_embeddings_batch([])
        assert result == []

    @pytest.mark.asyncio
    async def test_close(self, embedding_service):
        """Test closing the service."""
        # Should not raise
        await embedding_service.close()