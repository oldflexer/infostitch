"""Unit tests for Article entity."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from domain.entities.article import Article
from domain.value_objects.url import URL


class TestArticle:
    """Tests for Article entity."""

    def test_create_article(self):
        """Test creating an article with valid data."""
        article = Article(
            id=1,
            title="Test Article",
            url=URL.from_string("https://example.com/article/1"),
            summary="Test summary",
            published_at=datetime.now(timezone.utc),
            source_id=1,
            image_url="https://example.com/image.jpg",
        )
        
        assert article.id == 1
        assert article.title == "Test Article"
        assert str(article.url) == "https://example.com/article/1"
        assert article.summary == "Test summary"
        assert article.source_id == 1
        assert article.image_url == "https://example.com/image.jpg"

    def test_create_article_minimal(self):
        """Test creating an article with minimal required fields."""
        article = Article(
            id=1,
            title="Test Article",
            url=URL.from_string("https://example.com/article/1"),
            summary="Test summary",
            published_at=datetime.now(timezone.utc),
            source_id=1,
        )
        
        assert article.id == 1
        assert article.image_url is None

    def test_article_from_rss_entry(self):
        """Test creating article from RSS entry."""
        import feedparser
        
        feed = feedparser.parse("""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Test Feed</title>
        <item>
            <title>RSS Article Title</title>
            <link>https://example.com/rss/1</link>
            <description>RSS summary</description>
            <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
            <guid>https://example.com/rss/1</guid>
            <enclosure url="https://example.com/image.jpg" type="image/jpeg"/>
        </item>
    </channel>
</rss>""")
        
        entry = feed.entries[0]
        article = Article.from_rss_entry(entry, source_id=1)
        
        assert article.title == "RSS Article Title"
        assert str(article.url) == "https://example.com/rss/1"
        assert article.summary == "RSS summary"
        assert article.source_id == 1
        assert article.image_url == "https://example.com/image.jpg"

    def test_article_equality(self):
        """Test article equality - dataclass compares all fields."""
        url = URL.from_string("https://example.com/article/1")
        now = datetime.now(timezone.utc)
        article1 = Article(id=1, title="Title 1", url=url, summary="Summary 1", published_at=now, source_id=1, fetched_at=now)
        article2 = Article(id=1, title="Title 1", url=url, summary="Summary 1", published_at=now, source_id=1, fetched_at=now)
        article3 = Article(id=2, title="Title 2", url=url, summary="Summary 2", published_at=now, source_id=1, fetched_at=now)
        
        # Same fields = equal
        assert article1 == article2
        # Different fields = not equal
        assert article1 != article3
        
    def test_clean_url_property(self):
        """Test clean_url property."""
        article = Article(
            id=1,
            title="Test",
            url=URL.from_string("https://example.com/path?utm_source=test#fragment"),
            summary="Test",
            published_at=datetime.now(timezone.utc),
            source_id=1,
        )
        
        assert article.clean_url == "https://example.com/path"
        
    def test_domain_property(self):
        """Test domain property."""
        article = Article(
            id=1,
            title="Test",
            url=URL.from_string("https://example.com/path"),
            summary="Test",
            published_at=datetime.now(timezone.utc),
            source_id=1,
        )
        
        assert article.domain == "example.com"