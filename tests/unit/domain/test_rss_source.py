"""Unit tests for RssSource entity."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from domain.entities.rss_source import RssSource


class TestRssSource:
    """Tests for RssSource entity."""

    def test_create_rss_source(self):
        """Test creating an RSS source."""
        source = RssSource(
            id=1,
            url="https://example.com/feed.xml",
            enabled=True,
            last_fetch=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )

        assert source.id == 1
        assert source.url == "https://example.com/feed.xml"
        assert source.enabled is True
        assert source.last_fetch is not None

    def test_create_rss_source_invalid_url_raises(self):
        """Test that invalid URL raises ValueError."""
        with pytest.raises(ValueError, match="RSS source URL must be HTTP/HTTPS"):
            RssSource(
                id=1,
                url="not-a-url",
                enabled=True,
                created_at=datetime.now(timezone.utc),
            )

    def test_toggle_enabled(self):
        """Test toggling enabled status returns new source."""
        source = RssSource(
            id=1,
            url="https://example.com/feed.xml",
            enabled=True,
            created_at=datetime.now(timezone.utc),
        )

        assert source.enabled is True
        toggled = source.toggle_enabled()
        assert toggled.enabled is False
        assert toggled.id == source.id
        assert toggled.url == source.url

        toggled2 = toggled.toggle_enabled()
        assert toggled2.enabled is True

    def test_mark_fetched(self):
        """Test mark_fetched returns new source with updated last_fetch."""
        source = RssSource(
            id=1,
            url="https://example.com/feed.xml",
            enabled=True,
            created_at=datetime.now(timezone.utc),
        )

        assert source.last_fetch is None
        fetched = source.mark_fetched()
        assert fetched.last_fetch is not None
        assert fetched.id == source.id
