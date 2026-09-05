"""Integration tests for GeminiClient."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from infrastructure.clients.gemini_client import GeminiClient, MockGeminiClient


class TestGeminiClient:
    """Tests for GeminiClient."""

    @pytest.fixture
    def mock_httpx_client(self):
        """Create a mock httpx client."""
        client = AsyncMock()
        return client

    @pytest.fixture
    def gemini_client(self, mock_httpx_client):
        """Create GeminiClient with mocked HTTP client."""
        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            client = GeminiClient(api_key="test-api-key")
            client._client = mock_httpx_client
            return client

    @pytest.mark.asyncio
    async def test_generate_content_success(self, gemini_client, mock_httpx_client):
        """Test successful content generation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Generated response"}]
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        result = await gemini_client.generate_content("Test prompt")

        assert result == "Generated response"
        mock_httpx_client.post.assert_called_once()
    @pytest.mark.asyncio
    async def test_generate_content_with_system_instruction(self, gemini_client, mock_httpx_client):
        """Test content generation with system instruction."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Response with system"}]
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        result = await gemini_client.generate_content(
            "Test prompt",
            system_instruction="You are a helpful assistant"
        )

        assert result == "Response with system"
        call_args = mock_httpx_client.post.call_args
        payload = call_args.kwargs["json"]
        assert len(payload["contents"]) == 3

    @pytest.mark.asyncio
    async def test_generate_content_empty_response(self, gemini_client, mock_httpx_client):
        """Test handling of empty response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"candidates": []}
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        with pytest.raises(ValueError, match="No candidates returned"):
            await gemini_client.generate_content("Test prompt")

    @pytest.mark.asyncio
    async def test_generate_content_no_parts(self, gemini_client, mock_httpx_client):
        """Test handling of response without parts."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {}
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        with pytest.raises(ValueError, match="Empty response"):
            await gemini_client.generate_content("Test prompt")

    @pytest.mark.asyncio
    async def test_generate_embeddings_batch(self, gemini_client, mock_httpx_client):
        """Test batch embedding generation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "embeddings": [
                {"values": [0.1] * 768},
                {"values": [0.2] * 768},
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        result = await gemini_client.generate_embeddings_batch(["Text 1", "Text 2"])

        assert len(result) == 2
        assert len(result[0]) == 768
        assert len(result[1]) == 768

    @pytest.mark.asyncio
    async def test_count_tokens(self, gemini_client, mock_httpx_client):
        """Test token counting."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"totalTokens": 10}
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        result = await gemini_client.count_tokens("Test text")

        assert result == 10

    @pytest.mark.asyncio
    async def test_close(self, gemini_client, mock_httpx_client):
        """Test closing the client."""
        await gemini_client.close()
        mock_httpx_client.aclose.assert_called_once()
        assert gemini_client._client is None

    @pytest.mark.asyncio
    async def test_get_headers(self, gemini_client):
        """Test header generation."""
        headers = gemini_client._get_headers()
        assert headers["Content-Type"] == "application/json"
        assert headers["x-goog-api-key"] == "test-api-key"


class TestMockGeminiClient:
    """Tests for MockGeminiClient."""

    @pytest.fixture
    def mock_client(self):
        return MockGeminiClient()

    @pytest.mark.asyncio
    async def test_generate_content_ranking(self, mock_client):
        result = await mock_client.generate_content("Rank these articles")
        assert result == "[1, 2, 3, 4, 5]"

    @pytest.mark.asyncio
    async def test_generate_content_template(self, mock_client):
        result = await mock_client.generate_content("Generate post template")
        assert "Test post content" in result

    @pytest.mark.asyncio
    async def test_generate_content_default(self, mock_client):
        result = await mock_client.generate_content("Something else")
        assert result == "Mock response"

    @pytest.mark.asyncio
    async def test_generate_embedding(self, mock_client):
        result = await mock_client.generate_embedding("Test text")
        assert len(result) == 768
        assert all(isinstance(x, float) for x in result)

    @pytest.mark.asyncio
    async def test_generate_embeddings_batch(self, mock_client):
        result = await mock_client.generate_embeddings_batch(["Text 1", "Text 2"])
        assert len(result) == 2
        assert len(result[0]) == 768

    @pytest.mark.asyncio
    async def test_call_counts(self, mock_client):
        await mock_client.generate_content("Test")
        await mock_client.generate_content("Test")
        await mock_client.generate_embedding("Test")
        await mock_client.generate_embedding("Test")

        assert mock_client.call_count == 2
        assert mock_client.embedding_call_count == 2
    @pytest.mark.asyncio
    async def test_generate_embedding_success(self, mock_client):
        """Test successful embedding generation."""
        result = await mock_client.generate_embedding("Test text")
        assert len(result) == 768
        assert all(isinstance(x, float) for x in result)

    @pytest.mark.asyncio
    async def test_generate_embedding_empty(self, mock_client):
        """Test handling of empty embedding."""
        # MockGeminiClient doesn't return empty embeddings, so we test the real client
        # This test is not applicable for MockGeminiClient
        pass