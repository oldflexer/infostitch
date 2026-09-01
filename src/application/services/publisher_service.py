"""Publisher Service.

Manages publishing to multiple channels (Telegram, VK, Max).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from infrastructure.clients.max_client import MaxClient, MockMaxClient
from infrastructure.clients.telegram_client import TelegramClient, MockTelegramClient
from infrastructure.clients.vk_client import VKClient, MockVKClient
from infrastructure.config import get_settings


class PublisherClient:
    """Base publisher client interface."""

    async def send_message(self, text: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError

    async def close(self) -> None:
        pass


class TelegramPublisher(PublisherClient):
    """Telegram publisher."""

    def __init__(self, client: Optional[TelegramClient] = None):
        self._client = client or self._create_default_client()

    def _create_default_client(self) -> TelegramClient:
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


class VKPublisher(PublisherClient):
    """VK publisher."""

    def __init__(self, client: Optional[VKClient] = None):
        self._client = client or self._create_default_client()

    def _create_default_client(self) -> VKClient:
        settings = get_settings()
        configs = settings.get_channel_configs()
        vk_config = configs.get("vk", {})
        if not vk_config:
            return MockVKClient()
        return VKClient(
            access_token=vk_config.get("access_token_ref", ""),
            group_id=vk_config.get("group_id", ""),
            album_id=vk_config.get("album_id"),
        )

    async def send_message(
        self,
        text: str,
        image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        if image_url:
            return await self._client.post_with_photo(message=text, photo_url=image_url)
        return await self._client.wall_post(message=text)

    async def close(self) -> None:
        await self._client.close()


class MaxPublisher(PublisherClient):
    """Max (Odnoklassniki) publisher."""

    def __init__(self, client: Optional[MaxClient] = None):
        self._client = client or self._create_default_client()

    def _create_default_client(self) -> MaxClient:
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

    def __init__(self):
        self._publishers: Dict[str, PublisherClient] = {}
        self._init_publishers()

    def _init_publishers(self) -> None:
        settings = get_settings()
        configs = settings.get_channel_configs()

        if "telegram" in configs:
            self._publishers["telegram"] = TelegramPublisher()
        if "vk" in configs:
            self._publishers["vk"] = VKPublisher()
        if "max" in configs:
            self._publishers["max"] = MaxPublisher()

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