"""Gemini API Client.

Provides async interface to Google Gemini API for text generation and embeddings.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from infrastructure.config import get_settings


class GeminiClient:
    """Async client for Google Gemini API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-1.5-flash-latest",
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
    ):
        self._api_key = api_key or get_settings().gemini_api_key
        self._model = model
        self._base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(60.0, connect=10.0),
                limits=httpx.Limits(max_connections=10,
                                    max_keepalive_connections=5),
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @retry(
        wait=wait_exponential_jitter(initial=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        response_mime_type: str = "text/plain",
    ) -> str:
        """Generate text content using Gemini."""
        url = f"{self._base_url}/models/{self._model}:generateContent"

        parts = [{"text": prompt}]
        contents = [{"role": "user", "parts": parts}]

        if system_instruction:
            contents.insert(0, {"role": "user", "parts": [
                            {"text": system_instruction}]})
            contents.append(
                {"role": "model", "parts": [{"text": "Understood."}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens,
                "responseMimeType": response_mime_type,
            },
        }

        response = await self.client.post(
            url,
            headers=self._get_headers(),
            json=payload,
        )
        response.raise_for_status()

        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("No candidates returned from Gemini")

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            raise ValueError("Empty response from Gemini")

        return parts[0].get("text", "")

    @retry(
        wait=wait_exponential_jitter(initial=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def generate_embedding(
        self,
        text: str,
        model: str = "text-embedding-004",
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> List[float]:
        """Generate embedding for text."""
        url = f"{self._base_url}/models/{model}:embedContent"

        payload = {
            "content": {"parts": [{"text": text}]},
            "taskType": task_type,
        }

        response = await self.client.post(
            url,
            headers=self._get_headers(),
            json=payload,
        )
        response.raise_for_status()

        data = response.json()
        embedding = data.get("embedding", {})
        values = embedding.get("values", [])

        if not values:
            raise ValueError("Empty embedding returned from Gemini")

        return values

    @retry(
        wait=wait_exponential_jitter(initial=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def generate_embeddings_batch(
        self,
        texts: List[str],
        model: str = "text-embedding-004",
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        url = f"{self._base_url}/models/{model}:batchEmbedContents"

        requests = [
            {"content": {"parts": [{"text": text}]}, "taskType": task_type}
            for text in texts
        ]

        payload = {"requests": requests}

        response = await self.client.post(
            url,
            headers=self._get_headers(),
            json=payload,
        )
        response.raise_for_status()

        data = response.json()
        embeddings = []

        for emb_data in data.get("embeddings", []):
            values = emb_data.get("values", [])
            if not values:
                raise ValueError("Empty embedding in batch response")
            embeddings.append(values)

        return embeddings


    async def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        url = f"{self._base_url}/models/{self._model}:countTokens"

        payload = {"contents": [{"parts": [{"text": text}]}]}

        response = await self.client.post(
            url,
            headers=self._get_headers(),
            json=payload,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("totalTokens", 0)

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Content-Type": "application/json",
            "x-goog-api-key": self._api_key,
        }


class MockGeminiClient:
    """Mock Gemini client for testing."""

    def __init__(self, *args, **kwargs):
        self.call_count = 0
        self.embedding_call_count = 0

    async def close(self) -> None:
        pass

    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        response_mime_type: str = "text/plain",
    ) -> str:
        self.call_count += 1
        # Return mock response based on prompt content
        if "rank" in prompt.lower() or "select" in prompt.lower():
            return json.dumps([1, 2, 3, 4, 5])
        if "template" in prompt.lower() or "generate" in prompt.lower():
            return "📰 Test post content with <b>emphasis</b>. This is a test article summary."
        return "Mock response"

    async def generate_embedding(
        self,
        text: str,
        model: str = "text-embedding-004",
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> List[float]:
        self.embedding_call_count += 1
        # Return deterministic mock embedding based on text hash
        import hashlib
        hash_val = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        return [(hash_val >> i & 1) * 0.1 for i in range(768)]

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        model: str = "text-embedding-004",
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> List[List[float]]:
        return [await self.generate_embedding(t, model, task_type) for t in texts]
