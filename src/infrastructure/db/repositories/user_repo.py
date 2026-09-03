"""SQLAlchemy User Repository Implementation."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

import bcrypt

from domain.entities.user import User
from domain.repositories.user_repo import UserRepository
from infrastructure.db.sqlalchemy_models import User as UserModel


class SqlAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            password_hash=model.password_hash,
            role=model.role,
            created_at=model.created_at,
            last_login=model.last_login,
        )

    def _to_model(self, user: User) -> UserModel:
        return UserModel(
            id=user.id,
            username=user.username,
            password_hash=user.password_hash,
            role=user.role,
            created_at=user.created_at,
            last_login=user.last_login,
        )

    async def create(
        self, username: str, password: str, role: str = "admin"
    ) -> User:
        # Use bcrypt directly to avoid passlib issues
        password_hash = bcrypt.hashpw(password.encode(
            "utf-8"), bcrypt.gensalt()).decode("utf-8")
        model = UserModel(
            username=username,
            password_hash=password_hash,
            role=role,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self) -> List[User]:
        stmt = select(UserModel).order_by(UserModel.created_at)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def update(self, user: User) -> User:
        model = await self._session.get(UserModel, user.id)
        if not model:
            raise ValueError(f"User {user.id} not found")
        model.username = user.username
        model.password_hash = user.password_hash
        model.role = user.role
        model.last_login = user.last_login
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, user_id: int) -> bool:
        from sqlalchemy import delete
        stmt = delete(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def verify_password(self, username: str,
                              password: str) -> Optional[User]:
        user = await self.get_by_username(username)
        if user and bcrypt.checkpw(password.encode(
                "utf-8"), user.password_hash.encode("utf-8")):
            return user
        return None

    async def count(self) -> int:
        stmt = select(func.count(UserModel.id))
        result = await self._session.execute(stmt)
        return result.scalar() or 0
