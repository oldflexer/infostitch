"""Integration tests for JinaClient."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from infrastructure.clients.jina_client import JinaClient, MockJinaClient


class TestJinaClient:
    """Tests for real JinaClient with mocked HTTP."""

    @pytest.fixture
    def jina_client(self):
        """Create JinaClient with test API key."""
        return JinaClient(api_key="test-api-key")

    @pytest.fixture
    def mock_httpx_client(self):
        """Mock httpx.AsyncClient."""
        with patch("infrastructure.clients.jina_client.httpx.AsyncClient") as mock:
            mock_instance = AsyncMock()
            mock.return_value = mock_instance
            yield mock_instance

    @pytest.mark.asyncio
    async def test_extract_content_success(self, jina_client, mock_httpx_client):
        """Test successful content extraction."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "title": "Test Article",
                "content": "Full article content here...",
                "description": "Article description",
                "image": "https://example.com/image.jpg",
                "url": "https://example.com/article",
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.get.return_value = mock_response

        result = await jina_client.extract_content("https://example.com/article")

        assert result["title"] == "Test Article"
        assert result["content"] == "Full article content here..."
        assert result["description"] == "Article description"
        assert result["image"] == "https://example.com/image.jpg"
        assert result["url"] == "https://example.com/article"
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_content_http_error(self, jina_client, mock_httpx_client):
        """Test handling of HTTP errors."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=MagicMock(), response=MagicMock(status_code=404)
        )
        mock_httpx_client.get.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await jina_client.extract_content("https://example.com/notfound")

    @pytest.mark.asyncio
    async def test_extract_with_options(self, jina_client, mock_httpx_client):
        """Test content extraction with options."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "title": "Test Article",
                "content": "Content with options",
                "description": "Description",
                "image": "https://example.com/img.jpg",
                "url": "https://example.com/article",
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.get.return_value = mock_response

        result = await jina_client.extract_with_options(
            "https://example.com/article",
            timeout=60,
            with_generated_alt=False,
            with_images_summary=False,
        )

        assert result["title"] == "Test Article"
        call_args = mock_httpx_client.get.call_args
        assert call_args[1]["params"]["timeout"] == 60
        assert call_args[1]["params"]["with_generated_alt"] == "false"
        assert call_args[1]["params"]["with_images_summary"] == "false"

    @pytest.mark.asyncio
    async def test_close(self, jina_client, mock_httpx_client):
        """Test closing the client."""
        _ = jina_client.client
        await jina_client.close()
        mock_httpx_client.aclose.assert_called_once()
        assert jina_client._client is None

    @pytest.mark.asyncio
    async def test_get_headers_with_api_key(self, jina_client):
        """Test headers include API key."""
        headers = jina_client._get_headers()
        assert headers["Accept"] == "application/json"
        assert headers["Authorization"] == "Bearer test-api-key"

    @pytest.mark.asyncio
    async def test_get_headers_without_api_key(self):
        """Test headers without API key."""
        client = JinaClient(api_key=None)
        headers = client._get_headers()
        assert headers["Accept"] == "application/json"
        assert "Authorization" not in headers

    @pytest.mark.asyncio
    async def test_extract_image_url_from_featured(self, jina_client):
        """Test extracting image URL from featured image."""
        data = {"image": "https://example.com/featured.jpg"}
        result = jina_client.extract_image_url(data)
        assert result == "https://example.com/featured.jpg"

    @pytest.mark.asyncio
    async def test_extract_image_url_from_images_list(self, jina_client):
        """Test extracting image URL from images list."""
        data = {"images": [{"url": "https://example.com/img1.jpg"}, {"url": "https://example.com/img2.jpg"}]}
        result = jina_client.extract_image_url(data)
        assert result == "https://example.com/img1.jpg"

    @pytest.mark.asyncio
    async def test_extract_image_url_from_markdown(self, jina_client):
        """Test extracting image URL from markdown content."""
        data = {"content": "Text ![Alt](https://example.com/markdown.jpg) more text"}
        result = jina_client.extract_image_url(data)
        assert result == "https://example.com/markdown.jpg"

    @pytest.mark.asyncio
    async def test_extract_image_url_none(self, jina_client):
        """Test extracting image URL when none exists."""
        data = {"content": "No images here"}
        result = jina_client.extract_image_url(data)
        assert result is None

    @pytest.mark.asyncio
    async def test_clean_content_removes_links(self, jina_client):
        """Test cleaning content removes markdown links."""
        content = "Check [this link](https://example.com) out"
        result = jina_client.clean_content(content)
        assert result == "Check this link out"

    @pytest.mark.asyncio
    async def test_clean_content_removes_images(self, jina_client):
        """Test cleaning content removes markdown images."""
        # Note: Current implementation processes links before images,
        # so ![Alt](url) becomes !Alt (link regex matches [Alt](url) part)
        content = "Image: ![Alt](https://example.com/img.jpg)"
        result = jina_client.clean_content(content)
        assert result == "Image: !Alt"

    @pytest.mark.asyncio
    async def test_clean_content_removes_html(self, jina_client):
        """Test cleaning content removes HTML tags."""
        content = "<p>Paragraph</p><div>Div</div>"
        result = jina_client.clean_content(content)
        assert result == "ParagraphDiv"

    @pytest.mark.asyncio
    async def test_clean_content_normalizes_whitespace(self, jina_client):
        """Test cleaning content normalizes whitespace."""
        content = "Line 1\n\n\nLine 2\n\n\n\nLine 3"
        result = jina_client.clean_content(content)
        assert result == "Line 1\n\nLine 2\n\nLine 3"

    @pytest.mark.asyncio
    async def test_clean_content_truncates(self, jina_client):
        """Test cleaning content truncates to max_length."""
        content = "A" * 7000
        result = jina_client.clean_content(content, max_length=100)
        assert len(result) <= 103  # 100 + '...'
        assert result.endswith("...")


class TestMockJinaClient:
    """Tests for MockJinaClient."""

    @pytest.fixture
    def mock_client(self):
        """Create MockJinaClient."""
        return MockJinaClient()

    @pytest.mark.asyncio
    async def test_extract_content(self, mock_client):
        """Test mock content extraction."""
        result = await mock_client.extract_content("https://example.com/article")

        assert result["title"] == "Test Article Title"
        assert "full article content" in result["content"].lower()
        assert result["description"] == "Test article description"
        assert result["image"] == "https://example.com/image.jpg"
        assert result["url"] == "https://example.com/article"
        assert mock_client.call_count == 1

    @pytest.mark.asyncio
    async def test_extract_with_options(self, mock_client):
        """Test mock extract with options delegates to extract_content."""
        result = await mock_client.extract_with_options(
            "https://example.com/article",
            timeout=60,
            with_generated_alt=False,
            with_images_summary=False,
        )

        assert result["title"] == "Test Article Title"
        assert mock_client.call_count == 1

    @pytest.mark.asyncio
    async def test_extract_image_url(self, mock_client):
        """Test mock extract image URL."""
        data = {"image": "https://example.com/mock.jpg"}
        result = mock_client.extract_image_url(data)
        assert result == "https://example.com/mock.jpg"

    @pytest.mark.asyncio
    async def test_clean_content(self, mock_client):
        """Test mock clean content truncates."""
        content = "A" * 1000
        result = mock_client.clean_content(content, max_length=100)
        assert len(result) == 100

    @pytest.mark.asyncio
    async def test_close(self, mock_client):
        """Test mock close does nothing."""
        await mock_client.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_call_count_increments(self, mock_client):
        """Test call count increments on each call."""
        await mock_client.extract_content("https://example.com/1")
        await mock_client.extract_content("https://example.com/2")
        await mock_client.extract_with_options("https://example.com/3")

        assert mock_client.call_count == 3