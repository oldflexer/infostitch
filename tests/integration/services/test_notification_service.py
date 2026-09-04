"""Integration tests for NotificationService."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from application.services.notification_service import NotificationService
from infrastructure.clients.telegram_client import MockTelegramClient


class TestNotificationService:
    """Tests for NotificationService."""

    @pytest.fixture
    def mock_telegram_client(self):
        """Create a mock Telegram client."""
        return MockTelegramClient()

    @pytest.fixture
    def notification_service(self, mock_telegram_client):
        """Create NotificationService with mock client."""
        return NotificationService(client=mock_telegram_client)

    @pytest.mark.asyncio
    async def test_notify_error_success(
        self,
        notification_service,
        mock_telegram_client,
    ):
        """Test successful error notification."""
        error = ValueError("Test error message")
        context = {
            "correlation_id": "abc123",
            "step": "fetch_rss",
            "article_id": "1",
        }

        result = await notification_service.notify_error(error, context)

        assert result is True
        assert len(mock_telegram_client.sent_messages) == 1
        message = mock_telegram_client.sent_messages[0]["text"]
        assert "🚨 <b>ERROR</b>" in message
        assert "ValueError" in message
        assert "Test error message" in message
        assert "fetch_rss" in message
        assert "1" in message
        assert "abc123" in message

    @pytest.mark.asyncio
    async def test_notify_error_rate_limited(
        self,
        notification_service,
        mock_telegram_client,
    ):
        """Test error notification rate limiting."""
        error = ValueError("Test error message")
        context = {"correlation_id": "abc123", "step": "test", "article_id": "1"}

        # First notification should succeed
        result1 = await notification_service.notify_error(error, context)
        assert result1 is True

        # Second notification with same error should be rate limited
        result2 = await notification_service.notify_error(error, context)
        assert result2 is False
        assert len(mock_telegram_client.sent_messages) == 1

    @pytest.mark.asyncio
    async def test_notify_critical_success(
        self,
        notification_service,
        mock_telegram_client,
    ):
        """Test successful critical notification."""
        message = "Pipeline failed with 5 errors"
        context = {"correlation_id": "abc123"}

        result = await notification_service.notify_critical(message, context)

        assert result is True
        assert len(mock_telegram_client.sent_messages) == 1
        message_text = mock_telegram_client.sent_messages[0]["text"]
        assert "🔴 <b>CRITICAL</b>" in message_text
        assert "Pipeline failed with 5 errors" in message_text
        assert "abc123" in message_text

    @pytest.mark.asyncio
    async def test_notify_critical_bypasses_rate_limit(
        self,
        notification_service,
        mock_telegram_client,
    ):
        """Test critical notification bypasses rate limiting."""
        error = ValueError("Test error")
        context = {"correlation_id": "abc123", "step": "test", "article_id": "1"}

        # Send error notification (rate limited)
        await notification_service.notify_error(error, context)
        await notification_service.notify_error(error, context)  # rate limited

        # Critical should still go through
        result = await notification_service.notify_critical("Critical!", context)
        assert result is True
        assert len(mock_telegram_client.sent_messages) == 2  # error + critical

    @pytest.mark.asyncio
    async def test_notify_error_client_failure(
        self,
        notification_service,
    ):
        """Test error notification handles client failure."""
        # Replace client with one that fails
        failing_client = MagicMock()
        failing_client.send_message = AsyncMock(side_effect=Exception("Network error"))
        notification_service._client = failing_client

        error = ValueError("Test error")
        context = {"correlation_id": "abc123", "step": "test", "article_id": "1"}

        result = await notification_service.notify_error(error, context)

        assert result is False

    @pytest.mark.asyncio
    async def test_notify_error_with_severity(
        self,
        notification_service,
        mock_telegram_client,
    ):
        """Test error notification with different severities."""
        context = {"correlation_id": "abc123", "step": "test", "article_id": "1"}

        # Test WARNING severity
        error1 = RuntimeError("Runtime error 1")
        result = await notification_service.notify_error(error1, context, severity="WARNING")
        assert result is True
        message = mock_telegram_client.sent_messages[0]["text"]
        assert "🚨 <b>WARNING</b>" in message

        # Test CRITICAL severity (different error to avoid rate limiting)
        error2 = RuntimeError("Runtime error 2")
        result = await notification_service.notify_error(error2, context, severity="CRITICAL")
        assert result is True
        message = mock_telegram_client.sent_messages[1]["text"]
        assert "🚨 <b>CRITICAL</b>" in message

    @pytest.mark.asyncio
    async def test_close(self, notification_service, mock_telegram_client):
        """Test close method."""
        await notification_service.close()
        # Should not raise any exception