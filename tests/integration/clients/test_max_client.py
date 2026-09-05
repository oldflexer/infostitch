"""Integration tests for MaxClient."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from infrastructure.clients.max_client import MaxClient, MockMaxClient


class TestMaxClient:
    """Tests for real MaxClient with mocked HTTP."""

    @pytest.fixture
    def max_client(self):
        """Create MaxClient with test credentials."""
        return MaxClient(bot_token="test-token", chat_id="test-chat-id")

    @pytest.fixture
    def mock_httpx_client(self):
        """Mock httpx.AsyncClient."""
        with patch("infrastructure.clients.max_client.httpx.AsyncClient") as mock:
            mock_instance = AsyncMock()
            mock.return_value = mock_instance
            yield mock_instance

    @pytest.mark.asyncio
    async def test_send_message_success(self, max_client, mock_httpx_client):
        """Test successful message sending."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": True,
            "result": {"message_id": 123, "chat_id": "test-chat-id"},
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        result = await max_client.send_message("Hello, World!")

        assert result["message_id"] == 123
        mock_httpx_client.post.assert_called_once()
        call_args = mock_httpx_client.post.call_args
        assert call_args[1]["json"]["chat_id"] == "test-chat-id"
        assert call_args[1]["json"]["text"] == "Hello, World!"
        assert call_args[1]["json"]["parse_mode"] == "HTML"
        assert call_args[1]["json"]["disable_web_page_preview"] is True
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"
        assert call_args[1]["headers"]["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_send_message_with_custom_params(self, max_client, mock_httpx_client):
        """Test sending message with custom parse_mode and preview settings."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True, "result": {"message_id": 456}}
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        result = await max_client.send_message(
            "Test message",
            parse_mode="Markdown",
            disable_web_page_preview=False,
        )

        assert result["message_id"] == 456
        call_args = mock_httpx_client.post.call_args
        assert call_args[1]["json"]["parse_mode"] == "Markdown"
        assert call_args[1]["json"]["disable_web_page_preview"] is False

    @pytest.mark.asyncio
    async def test_send_message_api_error(self, max_client, mock_httpx_client):
        """Test handling of Max API error response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": False,
            "description": "Bad Request: chat not found",
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        with pytest.raises(RuntimeError, match="Max API error: Bad Request: chat not found"):
            await max_client.send_message("Test")

    @pytest.mark.asyncio
    async def test_send_message_http_error(self, max_client, mock_httpx_client):
        """Test handling of HTTP errors."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized", request=MagicMock(), response=MagicMock(status_code=401)
        )
        mock_httpx_client.post.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await max_client.send_message("Test")

    @pytest.mark.asyncio
    async def test_send_photo_success(self, max_client, mock_httpx_client):
        """Test successful photo sending."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": True,
            "result": {"message_id": 789, "photo": [{"file_id": "photo123"}]},
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        result = await max_client.send_photo(
            "https://example.com/photo.jpg",
            caption="Photo caption",
        )

        assert result["message_id"] == 789
        call_args = mock_httpx_client.post.call_args
        assert call_args[1]["json"]["chat_id"] == "test-chat-id"
        assert call_args[1]["json"]["photo_url"] == "https://example.com/photo.jpg"
        assert call_args[1]["json"]["caption"] == "Photo caption"
        assert call_args[1]["json"]["parse_mode"] == "HTML"

    @pytest.mark.asyncio
    async def test_send_photo_without_caption(self, max_client, mock_httpx_client):
        """Test sending photo without caption."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True, "result": {"message_id": 111}}
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        result = await max_client.send_photo("https://example.com/photo.jpg")

        assert result["message_id"] == 111
        call_args = mock_httpx_client.post.call_args
        assert call_args[1]["json"]["caption"] == ""

    @pytest.mark.asyncio
    async def test_send_photo_api_error(self, max_client, mock_httpx_client):
        """Test handling of Max API error for photo."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": False,
            "description": "Bad Request: wrong file identifier",
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        with pytest.raises(RuntimeError, match="Max API error: Bad Request: wrong file identifier"):
            await max_client.send_photo("https://example.com/bad.jpg")

    @pytest.mark.asyncio
    async def test_get_me_success(self, max_client, mock_httpx_client):
        """Test getting bot info."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": True,
            "result": {"id": 123456, "username": "test_bot", "first_name": "Test Bot"},
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.get.return_value = mock_response

        result = await max_client.get_me()

        assert result["id"] == 123456
        assert result["username"] == "test_bot"
        assert result["first_name"] == "Test Bot"
        mock_httpx_client.get.assert_called_once()
        call_args = mock_httpx_client.get.call_args
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"

    @pytest.mark.asyncio
    async def test_get_me_http_error(self, max_client, mock_httpx_client):
        """Test handling of HTTP error in get_me."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=MagicMock(), response=MagicMock(status_code=404)
        )
        mock_httpx_client.get.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await max_client.get_me()

    @pytest.mark.asyncio
    async def test_close(self, max_client, mock_httpx_client):
        """Test closing the client."""
        _ = max_client.client
        await max_client.close()
        mock_httpx_client.aclose.assert_called_once()
        assert max_client._client is None

    @pytest.mark.asyncio
    async def test_base_url_construction(self):
        """Test base URL is constructed correctly."""
        client = MaxClient(bot_token="123:ABC", chat_id="456")
        assert client._base_url == "https://botapi.max.ru"

    @pytest.mark.asyncio
    async def test_custom_base_url(self):
        """Test custom base URL."""
        client = MaxClient(
            bot_token="123:ABC",
            chat_id="456",
            base_url="https://custom.max.ru",
        )
        assert client._base_url == "https://custom.max.ru"

    @pytest.mark.asyncio
    async def test_get_headers(self, max_client):
        """Test headers include Bearer token."""
        headers = max_client._get_headers()
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Content-Type"] == "application/json"



class TestMockMaxClient:
    """Tests for MockMaxClient."""

    @pytest.fixture
    def mock_client(self):
        """Create MockMaxClient."""
        return MockMaxClient()

    @pytest.mark.asyncio
    async def test_send_message(self, mock_client):
        """Test mock message sending."""
        result = await mock_client.send_message("Hello, World!")

        assert result["ok"] is True
        assert result["message_id"] == 1
        assert len(mock_client.sent_messages) == 1
        assert mock_client.sent_messages[0]["text"] == "Hello, World!"
        assert mock_client.sent_messages[0]["parse_mode"] == "HTML"

    @pytest.mark.asyncio
    async def test_send_message_custom_params(self, mock_client):
        """Test mock message sending with custom params."""
        result = await mock_client.send_message(
            "Test",
            parse_mode="Markdown",
            disable_web_page_preview=False,
        )

        assert result["message_id"] == 1
        assert mock_client.sent_messages[0]["parse_mode"] == "Markdown"

    @pytest.mark.asyncio
    async def test_send_photo(self, mock_client):
        """Test mock photo sending."""
        result = await mock_client.send_photo(
            "https://example.com/photo.jpg",
            caption="Test caption",
        )

        assert result["ok"] is True
        assert result["message_id"] == 1
        assert len(mock_client.sent_photos) == 1
        assert mock_client.sent_photos[0]["photo_url"] == "https://example.com/photo.jpg"
        assert mock_client.sent_photos[0]["caption"] == "Test caption"

    @pytest.mark.asyncio
    async def test_send_photo_without_caption(self, mock_client):
        """Test mock photo sending without caption."""
        result = await mock_client.send_photo("https://example.com/photo.jpg")

        assert result["message_id"] == 1
        assert mock_client.sent_photos[0]["caption"] == ""

    @pytest.mark.asyncio
    async def test_get_me(self, mock_client):
        """Test mock get_me."""
        result = await mock_client.get_me()

        assert result["id"] == 123456
        assert result["username"] == "test_bot"
        assert result["first_name"] == "Test Bot"

    @pytest.mark.asyncio
    async def test_close(self, mock_client):
        """Test mock close does nothing."""
        await mock_client.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_multiple_messages(self, mock_client):
        """Test multiple messages are tracked."""
        await mock_client.send_message("Message 1")
        await mock_client.send_message("Message 2")
        await mock_client.send_message("Message 3")

        assert len(mock_client.sent_messages) == 3
        assert mock_client.sent_messages[0]["text"] == "Message 1"
        assert mock_client.sent_messages[1]["text"] == "Message 2"
        assert mock_client.sent_messages[2]["text"] == "Message 3"

    @pytest.mark.asyncio
    async def test_multiple_photos(self, mock_client):
        """Test multiple photos are tracked."""
        await mock_client.send_photo("https://example.com/1.jpg")
        await mock_client.send_photo("https://example.com/2.jpg")

        assert len(mock_client.sent_photos) == 2
        assert mock_client.sent_photos[0]["photo_url"] == "https://example.com/1.jpg"
        assert mock_client.sent_photos[1]["photo_url"] == "https://example.com/2.jpg"

