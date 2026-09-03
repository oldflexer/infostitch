"""Unit tests for URL value object."""
from __future__ import annotations

import pytest

from domain.value_objects.url import URL


class TestURL:
    """Tests for URL value object."""

    def test_from_string_valid(self):
        """Test creating URL from valid string."""
        url = URL.from_string("https://example.com/path?query=value#fragment")

        # Fragment is removed during normalization
        assert str(url) == "https://example.com/path?query=value"
        assert url.scheme == "https"
        assert url.domain == "example.com"
        assert url.path == "/path"
        assert url.query == "query=value"

    def test_from_string_without_scheme_raises(self):
        """Test that URL without scheme raises ValueError."""
        with pytest.raises(ValueError, match="Invalid URL"):
            URL.from_string("example.com/path")

    def test_from_string_http(self):
        """Test creating URL with http scheme."""
        url = URL.from_string("http://example.com/path")

        assert str(url) == "http://example.com/path"
        assert url.scheme == "http"

    def test_clean_for_dedup(self):
        """Test URL cleaning for deduplication."""
        # Remove fragment and normalize
        url = URL.from_string("https://example.com/path?query=value#fragment")
        clean = url.clean_for_dedup()

        assert clean == "https://example.com/path?query=value"
        assert "#fragment" not in clean

    def test_clean_for_dedup_removes_tracking_params(self):
        """Test that tracking parameters are removed."""
        url = URL.from_string(
            "https://example.com/path?utm_source=google&utm_medium=cpc&real_param=value")
        clean = url.clean_for_dedup()

        assert "utm_source" not in clean
        assert "utm_medium" not in clean
        assert "real_param=value" in clean

    def test_clean_for_dedup_removes_all_tracking(self):
        """Test that all tracking parameters are removed."""
        url = URL.from_string(
            "https://example.com/path?fbclid=123&gclid=456&ref=twitter&campaign_id=789&real=value")
        clean = url.clean_for_dedup()

        assert "fbclid" not in clean
        assert "gclid" not in clean
        assert "ref" not in clean
        assert "campaign_id" not in clean
        assert "real=value" in clean

    def test_normalization_removes_default_ports(self):
        """Test that default ports are removed."""
        url = URL.from_string("https://example.com:443/path")
        assert str(url) == "https://example.com/path"

        url = URL.from_string("http://example.com:80/path")
        assert str(url) == "http://example.com/path"

    def test_normalization_lowercases(self):
        """Test that scheme and domain are lowercased."""
        url = URL.from_string("HTTPS://EXAMPLE.COM/Path")
        assert str(url) == "https://example.com/Path"

    def test_trailing_slash_removed(self):
        """Test that trailing slash is removed from root path."""
        url = URL.from_string("https://example.com/")
        assert str(url) == "https://example.com"

    def test_equality(self):
        """Test URL equality."""
        url1 = URL.from_string("https://example.com/path")
        url2 = URL.from_string("https://example.com/path")
        url3 = URL.from_string("https://example.com/other")

        assert url1 == url2
        assert url1 != url3

    def test_hash(self):
        """Test URL is hashable."""
        url = URL.from_string("https://example.com/path")
        url_set = {url}

        assert url in url_set

    def test_domain_property(self):
        """Test domain property."""
        url = URL.from_string("https://example.com/path")
        assert url.domain == "example.com"

        url = URL.from_string("https://sub.example.com/path")
        assert url.domain == "sub.example.com"

    def test_path_property(self):
        """Test path property."""
        url = URL.from_string("https://example.com/path/to/resource")
        assert url.path == "/path/to/resource"

        url = URL.from_string("https://example.com")
        assert url.path == ""
