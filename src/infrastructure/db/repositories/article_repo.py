"""SQLAlchemy Article Repository Implementation."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.article import Article
from domain.repositories.article_repo import ArticleRepository
from infrastructure.db.sqlalchemy_models import RssSource as RssSourceModel


class SqlAlchemyArticleRepository(ArticleRepository):
    """SQLAlchemy implementation of ArticleRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, article: Article) -> Article:
        """Add a new article."""
        # For now, articles are not persisted separately
        # They are processed in-memory during pipeline
        # This is a placeholder for future persistence
        return article

    async def get_by_id(self, article_id: int) -> Optional[Article]:
        """Get article by ID."""
        # Not implemented - articles not persisted separately
        return None

    async def get_by_url(self, url: str) -> Optional[Article]:
        """Get article by URL."""
        return None

    async def get_by_source(
        self, source_id: int, limit: int = 100
    ) -> List[Article]:
        """Get articles by source ID."""
        return []

    async def get_recent(self, hours: int = 24, limit: int = 100) -> List[Article]:
        """Get recent articles."""
        return []

    async def get_unprocessed(self, limit: int = 100) -> List[Article]:
        """Get articles that haven't been processed yet."""
        return []

    async def update(self, article: Article) -> Article:
        """Update an existing article."""
        return article

    async def delete(self, article_id: int) -> bool:
        """Delete an article."""
        return False

    async def exists_by_url(self, url: str) -> bool:
        """Check if article exists by URL."""
        return False

    async def count_by_source(self, source_id: int) -> int:
        """Count articles by source."""
        return 0