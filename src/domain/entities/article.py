"""Article Entity.

Represents a raw article fetched from RSS feed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from domain.value_objects.url import URL


@dataclass(slots=True)
class Article:
    """Article entity - raw article from RSS feed."""

    id: Optional[int] = None
    source_id: Optional[int] = None
    title: str = ""
    url: URL = field(default_factory=lambda: URL("https://example.com"))
    published_at: Optional[datetime] = None
    summary: str = ""
    content: str = ""
    image_url: Optional[str] = None
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate article after initialization."""
        if not self.title:
            raise ValueError("Article title cannot be empty")
        if not isinstance(self.url, URL):
            raise ValueError("URL must be a URL value object")

    @property
    def clean_url(self) -> str:
        """Get URL normalized for deduplication."""
        return self.url.clean_for_dedup()

    @property
    def domain(self) -> str:
        """Get source domain."""
        return self.url.domain

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "title": self.title,
            "url": str(self.url),
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "summary": self.summary,
            "content": self.content,
            "image_url": self.image_url,
            "fetched_at": self.fetched_at.isoformat(),
        }

    @classmethod
    def from_rss_entry(cls, entry: dict, source_id: int) -> Article:
        """Create Article from feedparser entry."""
        from dateutil import parser as date_parser

        # Extract URL
        url = entry.get("link", "")
        if not url and "links" in entry:
            for link in entry["links"]:
                if link.get("rel") == "alternate" or link.get("type", "").startswith("text/html"):
                    url = link.get("href", "")
                    break

        # Extract published date
        published_at = None
        for date_field in ["published_parsed", "updated_parsed", "created_parsed"]:
            if date_field in entry and entry[date_field]:
                try:
                    published_at = datetime(*entry[date_field][:6], tzinfo=timezone.utc)
                    break
                except Exception:
                    pass

        # Fallback to string parsing
        if published_at is None:
            for date_field in ["published", "updated", "created"]:
                if date_field in entry and entry[date_field]:
                    try:
                        published_at = date_parser.parse(entry[date_field])
                        if published_at.tzinfo is None:
                            published_at = published_at.replace(tzinfo=timezone.utc)
                        break
                    except Exception:
                        pass

        # Extract summary
        summary = entry.get("summary", "") or entry.get("description", "")

        # Extract image
        image_url = None
        if "media_content" in entry:
            for media in entry["media_content"]:
                if media.get("type", "").startswith("image/"):
                    image_url = media.get("url")
                    break
        elif "media_thumbnail" in entry:
            image_url = entry["media_thumbnail"][0].get("url")
        elif "enclosures" in entry:
            for enc in entry["enclosures"]:
                if enc.get("type", "").startswith("image/"):
                    image_url = enc.get("href")
                    break

        return cls(
            source_id=source_id,
            title=entry.get("title", "").strip(),
            url=URL.from_string(url),
            published_at=published_at,
            summary=summary.strip(),
            content="",  # Will be filled by content extraction step
            image_url=image_url,
        )