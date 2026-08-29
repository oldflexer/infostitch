"""SQLAlchemy LLM Model Repository Implementation."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.llm_model import LLMModel
from domain.repositories.llm_model_repo import LLMModelRepository
from infrastructure.db.sqlalchemy_models import LLMModel as LLMModelModel


class SqlAlchemyLLMModelRepository(LLMModelRepository):
    """SQLAlchemy implementation of LLMModelRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: LLMModelModel) -> LLMModel:
        return LLMModel(
            id=model.id,
            name=model.name,
            provider=model.provider,
            model_id=model.model_id,
            api_key_ref=model.api_key_ref,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    def _to_model(self, model: LLMModel) -> LLMModelModel:
        return LLMModelModel(
            id=model.id,
            name=model.name,
            provider=model.provider,
            model_id=model.model_id,
            api_key_ref=model.api_key_ref,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    async def add(self, model: LLMModel) -> LLMModel:
        db_model = self._to_model(model)
        self._session.add(db_model)
        await self._session.flush()
        await self._session.refresh(db_model)
        return self._to_entity(db_model)

    async def get_by_id(self, model_id: int) -> Optional[LLMModel]:
        stmt = select(LLMModelModel).where(LLMModelModel.id == model_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_name(self, name: str) -> Optional[LLMModel]:
        stmt = select(LLMModelModel).where(LLMModelModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self, active_only: bool = False) -> List[LLMModel]:
        stmt = select(LLMModelModel).order_by(LLMModelModel.created_at)
        if active_only:
            stmt = stmt.where(LLMModelModel.is_active == True)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_active(self) -> List[LLMModel]:
        return await self.get_all(active_only=True)

    async def get_by_provider(self, provider: str) -> List[LLMModel]:
        stmt = select(LLMModelModel).where(LLMModelModel.provider == provider)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def update(self, model: LLMModel) -> LLMModel:
        db_model = await self._session.get(LLMModelModel, model.id)
        if not db_model:
            raise ValueError(f"LLM Model {model.id} not found")
        db_model.name = model.name
        db_model.provider = model.provider
        db_model.model_id = model.model_id
        db_model.api_key_ref = model.api_key_ref
        db_model.is_active = model.is_active
        await self._session.flush()
        await self._session.refresh(db_model)
        return self._to_entity(db_model)

    async def delete(self, model_id: int) -> bool:
        from sqlalchemy import delete
        stmt = delete(LLMModelModel).where(LLMModelModel.id == model_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def count(self) -> int:
        stmt = select(func.count(LLMModelModel.id))
        result = await self._session.execute(stmt)
        return result.scalar() or 0