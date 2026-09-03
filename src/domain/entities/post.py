"""Post Entity.

Represents a generated post ready for publishing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from domain.value_objects.embedding import Embedding
from domain.value_objects.template import Template
from domain.value_objects.url import URL


@dataclass(slots=True)
class Post:
    """Post entity - generated post ready for publishing."""

    id: Optional[int] = None
    article_id: Optional[int] = None
    source_id: Optional[int] = None
    channel_id: Optional[int] = None
    llm_model_id: Optional[int] = None
    template_id: Optional[str] = None
    title: str = ""
    summary: str = ""
    content: str = ""  # Full generated post text
    clean_url: str = ""
    embedding: Optional[Embedding] = None
    image_url: Optional[str] = None
    is_duplicate: bool = False
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate post after initialization."""
        if not self.title:
            raise ValueError("Post title cannot be empty")
        if not self.clean_url:
            raise ValueError("Post clean_url cannot be empty")

    @property
    def word_count(self) -> int:
        """Count words in post content."""
        return len(self.content.split())

    @property
    def char_count(self) -> int:
        """Count characters in post content."""
        return len(self.content)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "article_id": self.article_id,
            "source_id": self.source_id,
            "channel_id": self.channel_id,
            "llm_model_id": self.llm_model_id,
            "template_id": self.template_id,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "clean_url": self.clean_url,
            "embedding": self.embedding.vector if self.embedding else None,
            "image_url": self.image_url,
            "is_duplicate": self.is_duplicate,
            "created_at": self.created_at.isoformat(),
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }

    def with_embedding(self, embedding: Embedding) -> Post:
        """Return new Post with embedding set."""
        return Post(
            id=self.id,
            article_id=self.article_id,
            source_id=self.source_id,
            channel_id=self.channel_id,
            llm_model_id=self.llm_model_id,
            template_id=self.template_id,
            title=self.title,
            summary=self.summary,
            content=self.content,
            clean_url=self.clean_url,
            embedding=embedding,
            image_url=self.image_url,
            is_duplicate=self.is_duplicate,
            created_at=self.created_at,
            published_at=self.published_at,
        )

    def mark_duplicate(self) -> Post:
        """Return new Post marked as duplicate."""
        return Post(
            id=self.id,
            article_id=self.article_id,
            source_id=self.source_id,
            channel_id=self.channel_id,
            llm_model_id=self.llm_model_id,
            template_id=self.template_id,
            title=self.title,
            summary=self.summary,
            content=self.content,
            clean_url=self.clean_url,
            embedding=self.embedding,
            image_url=self.image_url,
            is_duplicate=True,
            created_at=self.created_at,
            published_at=self.published_at,
        )

    def mark_published(self, channel_id: int) -> Post:
        """Return new Post marked as published."""
        return Post(
            id=self.id,
            article_id=self.article_id,
            source_id=self.source_id,
            channel_id=channel_id,
            llm_model_id=self.llm_model_id,
            template_id=self.template_id,
            title=self.title,
            summary=self.summary,
            content=self.content,
            clean_url=self.clean_url,
            embedding=self.embedding,
            image_url=self.image_url,
            is_duplicate=self.is_duplicate,
            created_at=self.created_at,
            published_at=datetime.now(timezone.utc),
        )
