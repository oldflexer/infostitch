"""SQLAlchemy Post Repository Implementation."""
from __future__ import annotations

import math
from typing import List, Optional

from sqlalchemy import select, func, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.post import Post
from domain.repositories.post_repo import PostRepository
from domain.value_objects.embedding import Embedding
from infrastructure.db.sqlalchemy_models import PublishedPost as PublishedPostModel


class SqlAlchemyPostRepository(PostRepository):
    """SQLAlchemy implementation of PostRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: PublishedPostModel) -> Post:
        """Convert SQLAlchemy model to domain entity."""
        embedding = None
        if model.embedding:
            if isinstance(model.embedding, (bytes, bytearray)):
                embedding = Embedding.from_bytes(model.embedding)
            else:
                embedding = Embedding.from_list(model.embedding)

        return Post(
            id=model.id,
            article_id=None,
            source_id=model.source_id,
            channel_id=model.channel_id,
            llm_model_id=model.llm_model_id,
            template_id=model.template_id,
            title=model.title,
            summary=model.summary,
            content=model.post_text or "",
            clean_url=model.clean_url,
            embedding=embedding,
            image_url=model.image_url,
            is_duplicate=model.is_duplicate,
            created_at=model.created_at,
            published_at=model.created_at if not model.is_duplicate else None,
        )

    def _to_model(self, post: Post) -> PublishedPostModel:
        """Convert domain entity to SQLAlchemy model."""
        embedding_data = None
        if post.embedding:
            embedding_data = post.embedding.vector

        return PublishedPostModel(
            id=post.id,
            clean_url=post.clean_url,
            title=post.title,
            summary=post.summary,
            embedding=embedding_data,
            is_duplicate=post.is_duplicate,
            source_id=post.source_id,
            channel_id=post.channel_id,
            llm_model_id=post.llm_model_id,
            template_id=post.template_id,
            post_text=post.content,
            image_url=post.image_url,
            created_at=post.created_at,
        )

    async def add(self, post: Post) -> Post:
        """Add a new post."""
        model = self._to_model(post)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, post_id: int) -> Optional[Post]:
        """Get post by ID."""
async def get_recent(
        self, days: int = 5, limit: int = 100, exclude_duplicates: bool = True
    ) -> List[Post]:
        """Get recent posts."""
        from datetime import datetime, timezone, timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(PublishedPostModel)
            .where(PublishedPostModel.created_at >= cutoff)
            .order_by(PublishedPostModel.created_at.desc())
            .limit(limit)
        )

        if exclude_duplicates:
            stmt = stmt.where(PublishedPostModel.is_duplicate == False)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_source(
        self, source_id: int, limit: int = 100
    ) -> List[Post]:
        """Get posts by source ID."""
        stmt = (
            select(PublishedPostModel)
            .where(PublishedPostModel.source_id == source_id)
            .order_by(PublishedPostModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_channel(
        self, channel_id: int, limit: int = 100
    ) -> List[Post]:
        """Get posts by channel ID."""
        stmt = (
            select(PublishedPostModel)
            .where(PublishedPostModel.channel_id == channel_id)
            .order_by(PublishedPostModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_duplicates(self, limit: int = 100) -> List[Post]:
        """Get posts marked as duplicates."""
        stmt = (
            select(PublishedPostModel)
            .where(PublishedPostModel.is_duplicate == True)
async def update(self, post: Post) -> Post:
        """Update an existing post."""
        model = await self._session.get(PublishedPostModel, post.id)
        if not model:
            raise ValueError(f"Post {post.id} not found")

        model.clean_url = post.clean_url
        model.title = post.title
        model.summary = post.summary
        model.embedding = post.embedding.vector if post.embedding else None
        model.is_duplicate = post.is_duplicate
        model.source_id = post.source_id
        model.channel_id = post.channel_id
        model.llm_model_id = post.llm_model_id
        model.template_id = post.template_id
        model.post_text = post.content
        model.image_url = post.image_url

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, post_id: int) -> bool:
        """Delete a post."""
        stmt = delete(PublishedPostModel).where(PublishedPostModel.id == post_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def find_similar(
        self, embedding: Embedding, threshold: float = 0.75, days: int = 5
    ) -> Optional[Post]:
        """Find most similar post by embedding (semantic deduplication).

        Uses pgvector cosine similarity on PostgreSQL.
        Falls back to Python computation on SQLite.
        """
        from datetime import datetime, timezone, timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        # Check if we're using PostgreSQL with pgvector
        dialect_name = self._session.bind.dialect.name

        if dialect_name == "postgresql":
            # Use pgvector cosine similarity
            stmt = (
                select(PublishedPostModel)
                .where(
                    and_(
                        PublishedPostModel.is_duplicate == False,
                        PublishedPostModel.created_at >= cutoff,
                    )
                )
                .order_by(
                    PublishedPostModel.embedding.cosine_distance(embedding.vector)
                )
                .limit(1)
            )
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()

            if model and model.embedding:
                stored_embedding = Embedding.from_list(model.embedding)
                similarity = embedding.cosine_similarity(stored_embedding)
                if similarity >= threshold:
                    return self._to_entity(model)
            return None
        else:
            # SQLite fallback: load all and compute in Python
            stmt = select(PublishedPostModel).where(
                and_(
                    PublishedPostModel.is_duplicate == False,
                    PublishedPostModel.created_at >= cutoff,
                )
            )
            result = await self._session.execute(stmt)
            models = result.scalars().all()

            best_match = None
            best_similarity = 0.0

            for model in models:
                if model.embedding:
                    if isinstance(model.embedding, (bytes, bytearray)):
                        stored_embedding = Embedding.from_bytes(model.embedding)
                    else:
                        stored_embedding = Embedding.from_list(model.embedding)

                    similarity = embedding.cosine_similarity(stored_embedding)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = model

            if best_match and best_similarity >= threshold:
                return self._to_entity(best_match)
            return None

    async def count_recent(self, days: int = 5) -> int:
        """Count recent posts."""
        from datetime import datetime, timezone, timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = select(func.count(PublishedPostModel.id)).where(
            and_(
                PublishedPostModel.created_at >= cutoff,
                PublishedPostModel.is_duplicate == False,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def cleanup_old(self, days: int = 90) -> int:
        """Delete posts older than specified days. Returns count deleted."""
        from datetime import datetime, timezone, timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = delete(PublishedPostModel).where(
            PublishedPostModel.created_at < cutoff
        )
        result = await self._session.execute(stmt)
        return result.rowcount
            .order_by(PublishedPostModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]
        stmt = select(PublishedPostModel).where(PublishedPostModel.id == post_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_clean_url(self, clean_url: str) -> Optional[Post]:
        """Get post by clean URL (for deduplication)."""
        stmt = select(PublishedPostModel).where(
            PublishedPostModel.clean_url == clean_url
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None