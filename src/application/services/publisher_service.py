"""Publisher Service.

Manages publishing to multiple channels (Telegram, Max).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from infrastructure.clients.max_client import MaxClient, MockMaxClient
from infrastructure.clients.telegram_client import TelegramClient, MockTelegramClient
from infrastructure.clients.protocols import PublisherClientProtocol
from infrastructure.config import get_settings


class PublisherClient:
    """Base publisher client interface."""

    async def send_message(
            self, text: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError

    async def close(self) -> None:
        pass


class TelegramPublisher(PublisherClient):
    """Telegram publisher."""

    def __init__(self, client: Optional[PublisherClientProtocol] = None):
        self._client = client or self._create_default_client()

    def _create_default_client(self) -> PublisherClientProtocol:
        settings = get_settings()
        configs = settings.get_channel_configs()
        tg_config = configs.get("telegram", {})
        if not tg_config:
            return MockTelegramClient()
        return TelegramClient(
            bot_token=tg_config.get("bot_token_ref", ""),
            chat_id=tg_config.get("chat_id", ""),
        )

    async def send_message(
        self,
        text: str,
        image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        if image_url:
            return await self._client.send_photo(photo_url=image_url, caption=text)
        return await self._client.send_message(text=text)

    async def close(self) -> None:
        await self._client.close()


class MaxPublisher(PublisherClient):
    """Max (Odnoklassniki) publisher."""

    def __init__(self, client: Optional[PublisherClientProtocol] = None):
        self._client = client or self._create_default_client()

    def _create_default_client(self) -> PublisherClientProtocol:
        settings = get_settings()
        configs = settings.get_channel_configs()
        max_config = configs.get("max", {})
        if not max_config:
            return MockMaxClient()
        return MaxClient(
            bot_token=max_config.get("bot_token_ref", ""),
            chat_id=max_config.get("chat_id", ""),
        )

    async def send_message(
        self,
        text: str,
        image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        if image_url:
            return await self._client.send_photo(photo_url=image_url, caption=text)
        return await self._client.send_message(text=text)

    async def close(self) -> None:
        await self._client.close()


class PublisherService:
    """Service for publishing to multiple channels."""

    def __init__(
        self,
        telegram_client: Optional[PublisherClientProtocol] = None,
        max_client: Optional[PublisherClientProtocol] = None,
    ):
        self._publishers: Dict[str, PublisherClient] = {}
        self._telegram_client = telegram_client
        self._max_client = max_client
        self._init_publishers()

    def _init_publishers(self) -> None:
        settings = get_settings()
        configs = settings.get_channel_configs()
        print(f"DEBUG _init_publishers: configs = {configs}")

        if "telegram" in configs:
            print("DEBUG: Creating TelegramPublisher")
            self._publishers["telegram"] = TelegramPublisher(
                client=self._telegram_client)
        if "max" in configs:
            print("DEBUG: Creating MaxPublisher")
            self._publishers["max"] = MaxPublisher(client=self._max_client)

    def get_publisher(self, channel_type: str) -> Optional[PublisherClient]:
        """Get publisher for channel type."""
        return self._publishers.get(channel_type)

    def get_enabled_publishers(self) -> List[PublisherClient]:
        """Get all enabled publishers."""
        return list(self._publishers.values())

    async def publish_to_all(
        self,
        text: str,
        image_url: Optional[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """Publish to all enabled channels.

        Returns:
            Dict mapping channel_type to result (or error)
        """
        results = {}
        for channel_type, publisher in self._publishers.items():
            try:
                result = await publisher.send_message(text=text, image_url=image_url)
                results[channel_type] = {"success": True, "result": result}
            except Exception as e:
                results[channel_type] = {"success": False, "error": str(e)}
        return results

    async def close(self) -> None:
        for publisher in self._publishers.values():
            await publisher.close()
