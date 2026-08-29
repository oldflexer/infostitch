"""SQLAlchemy Channel Repository Implementation."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.channel import Channel
from domain.repositories.channel_repo import ChannelRepository
from infrastructure.db.sqlalchemy_models import Channel as ChannelModel


class SqlAlchemyChannelRepository(ChannelRepository):
    """SQLAlchemy implementation of ChannelRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: ChannelModel) -> Channel:
        return Channel(
            id=model.id,
            name=model.name,
            type=model.type,
            enabled=model.enabled,
            config=model.config_json,
            created_at=model.created_at,
        )

    def _to_model(self, channel: Channel) -> ChannelModel:
        return ChannelModel(
            id=channel.id,
            name=channel.name,
            type=channel.type,
            enabled=channel.enabled,
            config_json=channel.config,
            created_at=channel.created_at,
        )

    async def add(self, channel: Channel) -> Channel:
        model = self._to_model(channel)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, channel_id: int) -> Optional[Channel]:
        stmt = select(ChannelModel).where(ChannelModel.id == channel_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_name(self, name: str) -> Optional[Channel]:
        stmt = select(ChannelModel).where(ChannelModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self, enabled_only: bool = False) -> List[Channel]:
        stmt = select(ChannelModel).order_by(ChannelModel.created_at)
        if enabled_only:
            stmt = stmt.where(ChannelModel.enabled == True)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_enabled(self) -> List[Channel]:
        return await self.get_all(enabled_only=True)

    async def get_by_type(self, channel_type: str) -> List[Channel]:
        stmt = select(ChannelModel).where(ChannelModel.type == channel_type)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def update(self, channel: Channel) -> Channel:
        model = await self._session.get(ChannelModel, channel.id)
        if not model:
            raise ValueError(f"Channel {channel.id} not found")
        model.name = channel.name
        model.type = channel.type
        model.enabled = channel.enabled
        model.config_json = channel.config
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, channel_id: int) -> bool:
        from sqlalchemy import delete
        stmt = delete(ChannelModel).where(ChannelModel.id == channel_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def count(self) -> int:
        stmt = select(func.count(ChannelModel.id))
        result = await self._session.execute(stmt)
        return result.scalar() or 0