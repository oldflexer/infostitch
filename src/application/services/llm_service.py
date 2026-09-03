"""LLM Service.

Abstraction over LLM providers for text generation.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from infrastructure.clients.gemini_client import GeminiClient, MockGeminiClient
from infrastructure.config import get_settings


class LLMProvider(ABC):
    """Abstract LLM provider interface."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: str = "text",
    ) -> str:
        """Generate text from prompt."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close provider resources."""
        ...


class GeminiProvider(LLMProvider):
    """Gemini LLM provider."""

    def __init__(self, client: Optional[GeminiClient] = None):
        self._client = client or GeminiClient()

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: str = "text",
    ) -> str:
        mime_type = "application/json" if response_format == "json" else "text/plain"
        return await self._client.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type=mime_type,
        )

    async def close(self) -> None:
        await self._client.close()


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def __init__(self):
        self._client = MockGeminiClient()
        self.call_count = 0

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: str = "text",
    ) -> str:
        self.call_count += 1
        if "rank" in prompt.lower() or "select" in prompt.lower():
            import json
            return json.dumps([1, 2, 3, 4, 5])
        if "template" in prompt.lower() or "generate" in prompt.lower():
            return "📰 Test post content with <b>emphasis</b>. This is a test article summary."
        if response_format == "json":
            import json
            return json.dumps({"test": "value", "status": "ok"})
        return "Mock response"

    async def close(self) -> None:
        pass


class LLMService:
    """LLM Service - manages LLM providers and provides high-level interface."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        self._provider = provider or self._create_default_provider()

    def _create_default_provider(self) -> LLMProvider:
        settings = get_settings()
        if settings.app_env == "development" and not settings.gemini_api_key:
            return MockLLMProvider()
        return GeminiProvider()

    @property
    def provider(self) -> LLMProvider:
        return self._provider

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: str = "text",
    ) -> str:
        """Generate text using configured provider."""
        return await self._provider.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

    async def rank_articles(
        self,
        articles: List[Dict[str, Any]],
        recent_titles: List[str],
        max_count: int = 20,
    ) -> List[int]:
        """Rank articles by relevance using LLM."""
        articles_text = "\n".join(
            f"{i + 1}. {a['title']} - {a.get('summary', '')[:200]}"
            for i, a in enumerate(articles[:max_count])
        )

        recent_text = "\n".join(f"- {t}" for t in recent_titles[:10])

        prompt = f"""Rank the following articles by relevance for an AI/tech news channel.
Select up to {max_count} most interesting articles.
Avoid topics similar to recently published articles.

Recent titles:
{recent_text}

Candidates:
{articles_text}

Return ONLY a JSON array of selected article numbers (1-indexed), ordered by priority.
Example: [3, 1, 5, 2]"""

        system_instruction = """You are an expert AI/tech news curator.
Select the most engaging, timely, and diverse articles.
Prefer breaking news, major releases, and unique insights.
Avoid duplicate topics and minor updates."""

        response = await self.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.3,
            max_tokens=500,
            response_format="json",
        )

        try:
            import json
            selected = json.loads(response.strip())
            valid = [i for i in selected if 1 <= i <= len(articles)]
            return valid[:max_count]
        except Exception:
            return list(range(1, min(max_count, len(articles)) + 1))

    async def generate_post(
        self,
        template_prompt: str,
        article_data: Dict[str, str],
        min_length: int = 700,
        max_length: int = 730,
    ) -> Dict[str, str]:
        """Generate post using template."""
        prompt = template_prompt.format(
            title=article_data.get("title", ""),
            summary=article_data.get("summary", ""),
            content=article_data.get("content", ""),
            min_length=min_length,
            max_length=max_length,
        )

        system_instruction = """You are a professional tech news writer.
Write engaging, factual posts for a Telegram channel.
Follow all formatting requirements strictly."""

        post_text = await self.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.7,
            max_tokens=max_length + 100,
        )

        summary_prompt = f"""Write a 2-3 sentence summary of this article for embedding:
Title: {article_data.get('title', '')}
Content: {article_data.get('content', '')[:2000]}"""

        summary = await self.generate(
            prompt=summary_prompt,
            system_instruction="Write concise factual summary.",
            temperature=0.3,
            max_tokens=200,
        )

        return {
            "post_text": post_text.strip(),
            "summary": summary.strip(),
        }

    async def close(self) -> None:
        await self._provider.close()
