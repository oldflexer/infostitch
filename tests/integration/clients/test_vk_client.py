"""Integration tests for VKClient."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from infrastructure.clients.vk_client import MockVKClient, VKClient


class TestVKClient:
    """Tests for real VKClient with mocked HTTP."""

    @pytest.fixture
    def vk_client(self):
        """Create VKClient with test credentials."""
        return VKClient(access_token="test-token", group_id="12345")

    @pytest.fixture
    def mock_httpx_client(self):
        """Mock httpx.AsyncClient."""
        with patch("infrastructure.clients.vk_client.httpx.AsyncClient") as mock:
            mock_instance = AsyncMock()
            mock.return_value = mock_instance
            yield mock_instance

    @pytest.mark.asyncio
    async def test_get_wall_upload_server_success(self, vk_client, mock_httpx_client):
        """Test successful get wall upload server."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": {"upload_url": "https://vk.com/upload"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        result = await vk_client.get_wall_upload_server()

        assert result["upload_url"] == "https://vk.com/upload"
        mock_httpx_client.post.assert_called_once()
        call_args = mock_httpx_client.post.call_args
        assert call_args[0][0] == "https://api.vk.com/method/photos.getWallUploadServer"
        assert call_args[1]["data"]["access_token"] == "test-token"
        assert call_args[1]["data"]["v"] == "5.199"
        assert call_args[1]["data"]["group_id"] == "12345"

    @pytest.mark.asyncio
    async def test_get_wall_upload_server_api_error(self, vk_client, mock_httpx_client):
        """Test handling of VK API error."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": {"error_msg": "Invalid group_id"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        with pytest.raises(RuntimeError, match="VK API error: Invalid group_id"):
            await vk_client.get_wall_upload_server()

    @pytest.mark.asyncio
    async def test_get_wall_upload_server_http_error(self, vk_client, mock_httpx_client):
        """Test handling of HTTP error."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Server Error", request=MagicMock(), response=MagicMock(status_code=500)
        )
        mock_httpx_client.post.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await vk_client.get_wall_upload_server()

    @pytest.mark.asyncio
    async def test_upload_photo_success(self, vk_client):
        """Test successful photo upload."""
        import tempfile
        import os

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"fake_image_data")
            temp_path = f.name

        try:
            with patch("infrastructure.clients.vk_client.httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client

                mock_response = MagicMock()
                mock_response.json.return_value = {"server": 1, "photo": "photo_data", "hash": "hash123"}
                mock_response.raise_for_status = MagicMock()
                mock_client.post.return_value = mock_response

                result = await vk_client.upload_photo("https://vk.com/upload", temp_path)

                assert result["server"] == 1
                assert result["photo"] == "photo_data"
                assert result["hash"] == "hash123"
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_upload_photo_http_error(self, vk_client):
        """Test handling of HTTP error during upload."""
        import tempfile
        import os

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"fake_image_data")
            temp_path = f.name

        try:
            with patch("infrastructure.clients.vk_client.httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client

                mock_response = MagicMock()
                mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                    "400 Bad Request", request=MagicMock(), response=MagicMock(status_code=400)
                )
                mock_client.post.return_value = mock_response

                with pytest.raises(httpx.HTTPStatusError):
                    await vk_client.upload_photo("https://vk.com/upload", temp_path)
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_save_wall_photo_success(self, vk_client, mock_httpx_client):
        """Test successful save wall photo."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": [{"owner_id": -12345, "id": 67890}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        result = await vk_client.save_wall_photo(server=1, photo="photo_data", hash="hash123")

        assert result[0]["owner_id"] == -12345
        assert result[0]["id"] == 67890
        call_args = mock_httpx_client.post.call_args
        assert call_args[0][0] == "https://api.vk.com/method/photos.saveWallPhoto"
        assert call_args[1]["data"]["group_id"] == "12345"
        assert call_args[1]["data"]["server"] == 1
        assert call_args[1]["data"]["photo"] == "photo_data"
        assert call_args[1]["data"]["hash"] == "hash123"

    @pytest.mark.asyncio
    async def test_save_wall_photo_api_error(self, vk_client, mock_httpx_client):
        """Test handling of VK API error for save wall photo."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": {"error_msg": "Invalid hash"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        with pytest.raises(RuntimeError, match="VK API error: Invalid hash"):
            await vk_client.save_wall_photo(server=1, photo="photo_data", hash="bad_hash")

    @pytest.mark.asyncio
    async def test_wall_post_success(self, vk_client, mock_httpx_client):
        """Test successful wall post."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": {"post_id": 123}
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        result = await vk_client.wall_post(message="Test message")

        assert result["post_id"] == 123
        call_args = mock_httpx_client.post.call_args
        assert call_args[0][0] == "https://api.vk.com/method/wall.post"
        assert call_args[1]["data"]["owner_id"] == "-12345"
        assert call_args[1]["data"]["from_group"] == 1
        assert call_args[1]["data"]["message"] == "Test message"

    @pytest.mark.asyncio
    async def test_wall_post_with_attachments(self, vk_client, mock_httpx_client):
        """Test wall post with attachments."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": {"post_id": 456}}
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        result = await vk_client.wall_post(
            message="Test with photo",
            attachments="photo-12345_67890",
        )

        assert result["post_id"] == 456
        call_args = mock_httpx_client.post.call_args
        assert call_args[1]["data"]["attachments"] == "photo-12345_67890"

    @pytest.mark.asyncio
    async def test_wall_post_from_user(self, vk_client, mock_httpx_client):
        """Test wall post as user (not group)."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": {"post_id": 789}}
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        result = await vk_client.wall_post(message="User post", from_group=False)

        assert result["post_id"] == 789
        call_args = mock_httpx_client.post.call_args
        assert call_args[1]["data"]["from_group"] == 0

    @pytest.mark.asyncio
    async def test_wall_post_api_error(self, vk_client, mock_httpx_client):
        """Test handling of VK API error for wall post."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": {"error_msg": "Message too long"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        with pytest.raises(RuntimeError, match="VK API error: Message too long"):
            await vk_client.wall_post(message="Test")

    @pytest.mark.asyncio
    async def test_post_with_photo_success(self, vk_client):
        """Test successful post with photo."""
        with patch("infrastructure.clients.vk_client.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock photo download
            mock_response = MagicMock()
            mock_response.content = b"fake_image_data"
            mock_response.raise_for_status = MagicMock()
            mock_client.get.return_value = mock_response

            # Mock upload_photo
            with patch.object(vk_client, "get_wall_upload_server", new_callable=AsyncMock) as mock_get_server:
                mock_get_server.return_value = {"upload_url": "https://vk.com/upload"}

                with patch.object(vk_client, "upload_photo", new_callable=AsyncMock) as mock_upload:
                    mock_upload.return_value = {"server": 1, "photo": "photo_data", "hash": "hash123"}

                    with patch.object(vk_client, "save_wall_photo", new_callable=AsyncMock) as mock_save:
                        mock_save.return_value = [{"owner_id": -12345, "id": 67890}]

                        with patch.object(vk_client, "wall_post", new_callable=AsyncMock) as mock_wall_post:
                            mock_wall_post.return_value = {"post_id": 999}

                            result = await vk_client.post_with_photo(
                                message="Test with photo",
                                photo_url="https://example.com/photo.jpg",
                            )

                            assert result["post_id"] == 999
                            mock_get_server.assert_called_once()
                            mock_upload.assert_called_once()
                            mock_save.assert_called_once()
                            mock_wall_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_with_photo_download_error(self, vk_client):
        """Test handling of photo download error."""
        with patch("infrastructure.clients.vk_client.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=MagicMock(), response=MagicMock(status_code=404)
            )
            mock_client.get.return_value = mock_response

            with pytest.raises(httpx.HTTPStatusError):
                await vk_client.post_with_photo(
                    message="Test",
                    photo_url="https://example.com/notfound.jpg",
                )

    @pytest.mark.asyncio
    async def test_close(self, vk_client, mock_httpx_client):
        """Test closing the client."""
        _ = vk_client.client
        await vk_client.close()
        mock_httpx_client.aclose.assert_called_once()
        assert vk_client._client is None

    @pytest.mark.asyncio
    async def test_get_params(self, vk_client):
        """Test common request parameters."""
        params = vk_client._get_params()
        assert params["access_token"] == "test-token"
        assert params["v"] == "5.199"

    @pytest.mark.asyncio
    async def test_base_url_construction(self):
        """Test base URL is constructed correctly."""
        client = VKClient(access_token="token", group_id="123")
        assert client._base_url == "https://api.vk.com/method"

    @pytest.mark.asyncio
    async def test_custom_base_url(self):
        """Test custom base URL."""
        client = VKClient(
            access_token="token",
            group_id="123",
            base_url="https://custom.vk.com/method",
        )
        assert client._base_url == "https://custom.vk.com/method"

    @pytest.mark.asyncio
    async def test_custom_api_version(self):
        """Test custom API version."""
        client = VKClient(
            access_token="token",
            group_id="123",
            api_version="5.200",
        )
        assert client._api_version == "5.200"
        params = client._get_params()
        assert params["v"] == "5.200"

    @pytest.mark.asyncio
    async def test_album_id(self):
        """Test album_id parameter."""
        client = VKClient(
            access_token="token",
            group_id="123",
            album_id="456",
        )
        assert client._album_id == "456"



class TestMockVKClient:
    """Tests for MockVKClient."""

    @pytest.fixture
    def mock_client(self):
        """Create MockVKClient."""
        return MockVKClient()

    @pytest.mark.asyncio
    async def test_get_wall_upload_server(self, mock_client):
        """Test mock get wall upload server."""
        result = await mock_client.get_wall_upload_server()
        assert result["upload_url"] == "https://mock.vk.com/upload"

    @pytest.mark.asyncio
    async def test_upload_photo(self, mock_client):
        """Test mock upload photo."""
        result = await mock_client.upload_photo("https://vk.com/upload", "/path/to/photo.jpg")

        assert result["server"] == 1
        assert result["photo"] == "mock_photo"
        assert result["hash"] == "mock_hash"
        assert len(mock_client.uploaded_photos) == 1
        assert mock_client.uploaded_photos[0] == "/path/to/photo.jpg"

    @pytest.mark.asyncio
    async def test_save_wall_photo(self, mock_client):
        """Test mock save wall photo."""
        result = await mock_client.save_wall_photo(server=1, photo="photo_data", hash="hash123")

        assert result[0]["owner_id"] == -12345
        assert result[0]["id"] == 67890

    @pytest.mark.asyncio
    async def test_wall_post(self, mock_client):
        """Test mock wall post."""
        result = await mock_client.wall_post(message="Test message")

        assert result["post_id"] == 1
        assert len(mock_client.posts) == 1
        assert mock_client.posts[0]["message"] == "Test message"
        assert mock_client.posts[0]["attachments"] is None

    @pytest.mark.asyncio
    async def test_wall_post_with_attachments(self, mock_client):
        """Test mock wall post with attachments."""
        result = await mock_client.wall_post(
            message="Test with photo",
            attachments="photo-12345_67890",
        )

        assert result["post_id"] == 1
        assert mock_client.posts[0]["attachments"] == "photo-12345_67890"

    @pytest.mark.asyncio
    async def test_wall_post_from_user(self, mock_client):
        """Test mock wall post as user."""
        result = await mock_client.wall_post(message="User post", from_group=False)

        assert result["post_id"] == 1
        assert mock_client.posts[0]["message"] == "User post"

    @pytest.mark.asyncio
    async def test_post_with_photo(self, mock_client):
        """Test mock post with photo."""
        result = await mock_client.post_with_photo(
            message="Test with photo",
            photo_url="https://example.com/photo.jpg",
        )

        assert result["post_id"] == 1
        assert len(mock_client.posts) == 1
        assert mock_client.posts[0]["message"] == "Test with photo"
        assert mock_client.posts[0]["photo_url"] == "https://example.com/photo.jpg"

    @pytest.mark.asyncio
    async def test_close(self, mock_client):
        """Test mock close does nothing."""
        await mock_client.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_multiple_posts(self, mock_client):
        """Test multiple posts are tracked."""
        await mock_client.wall_post("Post 1")
        await mock_client.wall_post("Post 2")
        await mock_client.post_with_photo("Post 3", "https://example.com/photo.jpg")

        assert len(mock_client.posts) == 3
        assert mock_client.posts[0]["message"] == "Post 1"
        assert mock_client.posts[1]["message"] == "Post 2"
        assert mock_client.posts[2]["message"] == "Post 3"

    @pytest.mark.asyncio
    async def test_multiple_uploads(self, mock_client):
        """Test multiple photo uploads are tracked."""
        await mock_client.upload_photo("https://vk.com/upload", "/path/1.jpg")
        await mock_client.upload_photo("https://vk.com/upload", "/path/2.jpg")

        assert len(mock_client.uploaded_photos) == 2
        assert mock_client.uploaded_photos[0] == "/path/1.jpg"
        assert mock_client.uploaded_photos[1] == "/path/2.jpg"

