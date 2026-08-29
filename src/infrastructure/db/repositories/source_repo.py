"""SQLAlchemy Source Repository Implementation."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.rss_source import RssSource
from domain.repositories.source_repo import SourceRepository
from infrastructure.db.sqlalchemy_models import RssSource as RssSourceModel


class SqlAlchemySourceRepository(SourceRepository):
    """SQLAlchemy implementation of SourceRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: RssSourceModel) -> RssSource:
        return RssSource(
            id=model.id,
            url=model.url,
            enabled=model.enabled,
            last_fetch=model.last_fetch,
            created_at=model.created_at,
        )

    def _to_model(self, source: RssSource) -> RssSourceModel:
        return RssSourceModel(
            id=source.id,
            url=source.url,
            enabled=source.enabled,
            last_fetch=source.last_fetch,
            created_at=source.created_at,
        )

    async def add(self, source: RssSource) -> RssSource:
        model = self._to_model(source)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, source_id: int) -> Optional[RssSource]:
        stmt = select(RssSourceModel).where(RssSourceModel.id == source_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_url(self, url: str) -> Optional[RssSource]:
        stmt = select(RssSourceModel).where(RssSourceModel.url == url)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self, enabled_only: bool = False) -> List[RssSource]:
        stmt = select(RssSourceModel).order_by(RssSourceModel.created_at)
        if enabled_only:
            stmt = stmt.where(RssSourceModel.enabled == True)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_enabled(self) -> List[RssSource]:
        return await self.get_all(enabled_only=True)

    async def update(self, source: RssSource) -> RssSource:
        model = await self._session.get(RssSourceModel, source.id)
        if not model:
            raise ValueError(f"Source {source.id} not found")
        model.url = source.url
        model.enabled = source.enabled
        model.last_fetch = source.last_fetch
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, source_id: int) -> bool:
        from sqlalchemy import delete
        stmt = delete(RssSourceModel).where(RssSourceModel.id == source_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def update_last_fetch(self, source_id: int) -> bool:
        from datetime import datetime, timezone
        stmt = (
            update(RssSourceModel)
            .where(RssSourceModel.id == source_id)
            .values(last_fetch=datetime.now(timezone.utc))
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def count(self) -> int:
        stmt = select(func.count(RssSourceModel.id))
        result = await self._session.execute(stmt)
        return result.scalar() or 0