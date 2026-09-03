"""Max (Odnoklassniki) API Client.

Provides async interface to Max API for sending messages.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter


class MaxClient:
    """Async client for Max (Odnoklassniki) API."""

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        base_url: str = "https://botapi.max.ru",
    ):
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=10.0),
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self._bot_token}",
            "Content-Type": "application/json",
        }

    @retry(
        wait=wait_exponential_jitter(initial=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def send_message(
        self,
        text: str,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = True,
    ) -> Dict[str, Any]:
        """Send text message to chat.

        Args:
            text: Message text
            parse_mode: Parse mode (HTML, Markdown)
            disable_web_page_preview: Disable link previews

        Returns:
            API response
        """
        url = f"{self._base_url}/messages"

        payload = {
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }

        response = await self.client.post(
            url,
            headers=self._get_headers(),
            json=payload,
        )
        response.raise_for_status()

        data = response.json()
        if not data.get("ok", True):
            raise RuntimeError(
                f"Max API error: {data.get('description', 'Unknown error')}")

        return data.get("result", {})

    @retry(
        wait=wait_exponential_jitter(initial=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def send_photo(
        self,
        photo_url: str,
        caption: str = "",
        parse_mode: str = "HTML",
    ) -> Dict[str, Any]:
        """Send photo with caption to chat.

        Args:
            photo_url: Photo URL
            caption: Photo caption
            parse_mode: Parse mode for caption

        Returns:
            API response
        """
        url = f"{self._base_url}/messages"

        payload = {
            "chat_id": self._chat_id,
            "photo_url": photo_url,
            "caption": caption,
            "parse_mode": parse_mode,
        }

        response = await self.client.post(
            url,
            headers=self._get_headers(),
            json=payload,
        )
        response.raise_for_status()

        data = response.json()
        if not data.get("ok", True):
            raise RuntimeError(
                f"Max API error: {data.get('description', 'Unknown error')}")

        return data.get("result", {})

    async def get_me(self) -> Dict[str, Any]:
        """Get bot info."""
        url = f"{self._base_url}/getMe"
        response = await self.client.get(
            url,
            headers=self._get_headers(),
        )
        response.raise_for_status()
        data = response.json()
        return data.get("result", {})


class MockMaxClient:
    """Mock Max client for testing."""

    def __init__(self, *args, **kwargs):
        self.sent_messages = []
        self.sent_photos = []

    async def close(self) -> None:
        pass

    async def send_message(
        self,
        text: str,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = True,
    ) -> Dict[str, Any]:
        self.sent_messages.append({
            "text": text,
            "parse_mode": parse_mode,
        })
        return {"message_id": len(self.sent_messages), "ok": True}

    async def send_photo(
        self,
        photo_url: str,
        caption: str = "",
        parse_mode: str = "HTML",
    ) -> Dict[str, Any]:
        self.sent_photos.append({
            "photo_url": photo_url,
            "caption": caption,
        })
        return {"message_id": len(self.sent_photos), "ok": True}

    async def get_me(self) -> Dict[str, Any]:
        return {"id": 123456, "username": "test_bot", "first_name": "Test Bot"}
