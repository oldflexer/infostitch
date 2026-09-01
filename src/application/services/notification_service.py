"""Notification Service for Error Alerts.

Sends critical error notifications via Telegram.
"""
from __future__ import annotations

import asyncio
from typing import Optional

import structlog

from infrastructure.clients.telegram_client import TelegramClient, MockTelegramClient
from infrastructure.config import get_settings

logger = structlog.get_logger(__name__)


class NotificationService:
    """Service for sending error notifications."""
    
    def __init__(self, client: Optional[TelegramClient] = None):
        self._client = client or self._create_default_client()
        self._rate_limiter: dict[str, float] = {}
        self._min_interval = 60.0  # Minimum seconds between same error notifications
    
    def _create_default_client(self) -> TelegramClient:
        settings = get_settings()
        configs = settings.get_channel_configs()
        tg_config = configs.get("telegram", {})
        if not tg_config:
            return MockTelegramClient()
        return TelegramClient(
            bot_token=tg_config.get("bot_token_ref", ""),
            chat_id=tg_config.get("notification_chat_id", tg_config.get("chat_id", "")),
        )
    
    async def notify_error(
        self,
        error: Exception,
        context: dict,
        severity: str = "ERROR",
    ) -> bool:
        """Send error notification.
        
        Args:
            error: The exception that occurred
            context: Additional context (step, article_id, correlation_id, etc.)
            severity: Error severity (ERROR, CRITICAL)
        
        Returns:
            True if notification was sent, False otherwise
        """
        # Rate limiting
        error_key = f"{type(error).__name__}:{str(error)[:100]}"
        import time
        now = time.time()
        if error_key in self._rate_limiter:
            if now - self._rate_limiter[error_key] < self._min_interval:
                logger.debug("Notification rate limited", error_key=error_key)
                return False
        self._rate_limiter[error_key] = now
        
        # Format message
        correlation_id = context.get("correlation_id", "unknown")
        step = context.get("step", "unknown")
        article_id = context.get("article_id", "unknown")
        
        message = (
            f"🚨 <b>{severity}</b>: {type(error).__name__}\n"
            f"<b>Message:</b> {str(error)[:500]}\n"
            f"<b>Step:</b> {step}\n"
            f"<b>Article:</b> {article_id}\n"
            f"<b>Correlation ID:</b> {correlation_id}\n"
        )
        
        try:
            await self._client.send_message(message, parse_mode="HTML")
            logger.info("Error notification sent", severity=severity, correlation_id=correlation_id)
            return True
        except Exception as e:
            logger.error("Failed to send error notification", error=str(e))
            return False
    
    async def notify_critical(
        self,
        message: str,
        context: dict,
    ) -> bool:
        """Send critical notification (bypasses rate limiting)."""
        correlation_id = context.get("correlation_id", "unknown")
        full_message = f"🔴 <b>CRITICAL</b>\n{message}\n<b>Correlation ID:</b> {correlation_id}"
        
        try:
            await self._client.send_message(full_message, parse_mode="HTML")
            logger.critical("Critical notification sent", correlation_id=correlation_id)
            return True
        except Exception as e:
            logger.error("Failed to send critical notification", error=str(e))
            return False
    
    async def close(self) -> None:
        await self._client.close()