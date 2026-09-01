"""Telegram Bot API Client.

Provides async interface to Telegram Bot API for sending messages and photos.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter


class TelegramClient:
    """Async client for Telegram Bot API."""

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        base_url: str = "https://api.telegram.org/bot",
    ):
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._base_url = f"{base_url}{bot_token}"
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
        url = f"{self._base_url}/sendMessage"

        payload = {
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }

        response = await self.client.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(f"Telegram API error: {data.get('description')}")

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
            photo_url: Photo URL or file_id
            caption: Photo caption
            parse_mode: Parse mode for caption

        Returns:
            API response
        """
        url = f"{self._base_url}/sendPhoto"

        payload = {
            "chat_id": self._chat_id,
            "photo": photo_url,
            "caption": caption,
            "parse_mode": parse_mode,
        }

        response = await self.client.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(f"Telegram API error: {data.get('description')}")

        return data.get("result", {})

    @retry(
        wait=wait_exponential_jitter(initial=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def send_document(
        self,
        document_url: str,
        caption: str = "",
        parse_mode: str = "HTML",
    ) -> Dict[str, Any]:
        """Send document to chat."""
        url = f"{self._base_url}/sendDocument"

        payload = {
            "chat_id": self._chat_id,
            "document": document_url,
            "caption": caption,
            "parse_mode": parse_mode,
        }

        response = await self.client.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(f"Telegram API error: {data.get('description')}")

        return data.get("result", {})

    async def get_me(self) -> Dict[str, Any]:
        """Get bot info."""
        url = f"{self._base_url}/getMe"
        response = await self.client.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("result", {})


class MockTelegramClient:
    """Mock Telegram client for testing."""

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

    async def send_document(
        self,
        document_url: str,
        caption: str = "",
        parse_mode: str = "HTML",
    ) -> Dict[str, Any]:
        return {"message_id": 1, "ok": True}

    async def get_me(self) -> Dict[str, Any]:
        return {"id": 123456, "username": "test_bot", "first_name": "Test Bot"}