"""Unit tests for Post entity."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from domain.entities.post import Post
from domain.value_objects.embedding import Embedding


class TestPost:
    """Tests for Post entity."""

    def test_create_post(self):
        """Test creating a post with valid data."""
        embedding = Embedding.from_list([0.1] * 768)
        post = Post(
            id=1,
            title="Test Post",
            summary="Test summary",
            content="Test content",
            clean_url="https://example.com/post/1",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=datetime.now(timezone.utc),
        )

        assert post.id == 1
        assert post.title == "Test Post"
        assert post.summary == "Test summary"
        assert post.content == "Test content"
        assert post.clean_url == "https://example.com/post/1"
        assert post.embedding is not None
        assert isinstance(post.embedding, Embedding)
        assert post.is_duplicate is False
        assert post.source_id == 1
        assert post.channel_id == 1
        assert post.llm_model_id == 1
        assert post.template_id == "news_brief"
        assert post.published_at is None  # Defaults to None

    def test_post_duplicate_flag(self):
        """Test post duplicate flag."""
        embedding = Embedding.from_list([0.1] * 768)
        post = Post(
            id=1,
            title="Test Post",
            summary="Test summary",
            content="Test content",
            clean_url="https://example.com/post/1",
            embedding=embedding,
            is_duplicate=True,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=datetime.now(timezone.utc),
        )

        assert post.is_duplicate is True

    def test_post_published_at_explicit(self):
        """Test post published_at when explicitly set."""
        embedding = Embedding.from_list([0.1] * 768)
        now = datetime.now(timezone.utc)

        # Post with explicit published_at
        post1 = Post(
            id=1,
            title="Test Post",
            summary="Test summary",
            content="Test content",
            clean_url="https://example.com/post/1",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
            published_at=now,
        )
        assert post1.published_at == now

        # Post without published_at (defaults to None)
        post2 = Post(
            id=2,
            title="Test Post 2",
            summary="Test summary 2",
            content="Test content 2",
            clean_url="https://example.com/post/2",
            embedding=embedding,
            is_duplicate=True,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )
        assert post2.published_at is None

    def test_mark_published(self):
        """Test mark_published returns new post with published_at set."""
        embedding = Embedding.from_list([0.1] * 768)
        now = datetime.now(timezone.utc)

        post = Post(
            id=1,
            title="Test Post",
            summary="Test summary",
            content="Test content",
            clean_url="https://example.com/post/1",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )

        published = post.mark_published(channel_id=1)
        assert published.published_at is not None
        assert published.channel_id == 1
        assert published.id == post.id
        assert published.title == post.title

    def test_mark_duplicate(self):
        """Test mark_duplicate returns new post with is_duplicate=True."""
        embedding = Embedding.from_list([0.1] * 768)
        now = datetime.now(timezone.utc)

        post = Post(
            id=1,
            title="Test Post",
            summary="Test summary",
            content="Test content",
            clean_url="https://example.com/post/1",
            embedding=embedding,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )

        duplicated = post.mark_duplicate()
        assert duplicated.is_duplicate is True
        assert duplicated.id == post.id

    def test_with_embedding(self):
        """Test with_embedding returns new post with embedding set."""
        embedding1 = Embedding.from_list([0.1] * 768)
        embedding2 = Embedding.from_list([0.2] * 768)
        now = datetime.now(timezone.utc)

        post = Post(
            id=1,
            title="Test Post",
            summary="Test summary",
            content="Test content",
            clean_url="https://example.com/post/1",
            embedding=embedding1,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=now,
        )

        updated = post.with_embedding(embedding2)
        assert updated.embedding == embedding2
        assert updated.id == post.id
