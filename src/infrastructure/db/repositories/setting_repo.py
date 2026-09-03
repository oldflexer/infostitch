"""SQLAlchemy Setting Repository Implementation."""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from sqlalchemy import select, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from domain.repositories.setting_repo import SettingRepository
from infrastructure.db.sqlalchemy_models import Setting as SettingModel
from infrastructure.config import DEFAULT_SETTINGS


class SqlAlchemySettingRepository(SettingRepository):
    """SQLAlchemy implementation of SettingRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, key: str) -> Optional[str]:
        stmt = select(SettingModel.value).where(SettingModel.key == key)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> Dict[str, str]:
        stmt = select(SettingModel.key, SettingModel.value)
        result = await self._session.execute(stmt)
        return {row.key: row.value for row in result.all()}

    async def set(self, key: str, value: str, description: str = "") -> None:
        # Upsert: insert or update
        dialect = self._session.bind.dialect.name
        if dialect == "postgresql":
            stmt = pg_insert(SettingModel).values(
                key=key, value=value, description=description
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["key"],
                set_=dict(value=value, description=description),
            )
        else:
            # SQLite
            stmt = sqlite_insert(SettingModel).values(
                key=key, value=value, description=description
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["key"],
                set_=dict(value=value, description=description),
            )
        await self._session.execute(stmt)

    async def delete(self, key: str) -> bool:
        stmt = delete(SettingModel).where(SettingModel.key == key)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def exists(self, key: str) -> bool:
        stmt = select(SettingModel.key).where(SettingModel.key == key)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def bulk_set(self, settings: Dict[str, str]) -> None:
        for key, value in settings.items():
            await self.set(key, value)

    async def get_typed(self, key: str, default: Any = None) -> Any:
        value = await self.get(key)
        if value is None:
            return default

        # Try JSON
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            pass

        # Try boolean
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # Try int
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        return value

    async def initialize_defaults(
            self, defaults: Dict[str, str] = None) -> None:
        """Initialize default settings if not present."""
        settings_to_set = defaults or DEFAULT_SETTINGS
        for key, value in settings_to_set.items():
            if not await self.exists(key):
                await self.set(key, value)
