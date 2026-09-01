"""Log Repository Interface and Implementation.

Provides data access for structured application logs.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.log import Log
from infrastructure.db.sqlalchemy_models import Log as LogModel


@dataclass
class LogFilters:
    """Filters for log queries."""
    level: Optional[str] = None
    module: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    correlation_id: Optional[str] = None
    search_query: Optional[str] = None


@dataclass
class Pagination:
    """Pagination parameters."""
    page: int = 1
    page_size: int = 50
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        return self.page_size


class LogRepository(ABC):
    """Abstract repository for Log entities."""

    @abstractmethod
    async def add(self, log: Log) -> Log:
        """Add a new log entry."""
        ...

    @abstractmethod
    async def get_by_id(self, log_id: int) -> Optional[Log]:
        """Get log by ID."""
        ...

    @abstractmethod
    async def get_logs(
        self,
        filters: Optional[LogFilters] = None,
        pagination: Optional[Pagination] = None,
    ) -> List[Log]:
        """Get logs with filters and pagination."""
        ...

    @abstractmethod
    async def count_logs(self, filters: Optional[LogFilters] = None) -> int:
        """Count logs matching filters."""
        ...

    @abstractmethod
    async def get_log_stats(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get log statistics."""
        ...

    @abstractmethod
    async def search_logs(
        self,
        query: str,
        filters: Optional[LogFilters] = None,
        pagination: Optional[Pagination] = None,
    ) -> List[Log]:
        """Search logs with full-text query."""
        ...
class SqlAlchemyLogRepository(LogRepository):
    """SQLAlchemy implementation of LogRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: LogModel) -> Log:
        return Log(
            id=model.id,
            timestamp=model.timestamp,
            level=model.level,
            module=model.module,
            message=model.message,
            context_json=model.context_json,
            user_id=model.user_id,
        )

    async def add(self, log: Log) -> Log:
        model = LogModel(
            timestamp=log.timestamp,
            level=log.level,
            module=log.module,
            message=log.message,
            context_json=log.context_json,
            user_id=log.user_id,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, log_id: int) -> Optional[Log]:
        stmt = select(LogModel).where(LogModel.id == log_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_logs(
        self,
        filters: Optional[LogFilters] = None,
        pagination: Optional[Pagination] = None,
    ) -> List[Log]:
        stmt = select(LogModel).order_by(desc(LogModel.timestamp))
        
        if filters:
            conditions = []
            if filters.level:
                conditions.append(LogModel.level == filters.level)
            if filters.module:
                conditions.append(LogModel.module == filters.module)
            if filters.start_time:
                conditions.append(LogModel.timestamp >= filters.start_time)
            if filters.end_time:
                conditions.append(LogModel.timestamp <= filters.end_time)
            if filters.correlation_id:
                conditions.append(
                    LogModel.context_json.op('->>')('correlation_id') == filters.correlation_id
                )
            if filters.search_query:
                conditions.append(
                    LogModel.message.ilike(f"%{filters.search_query}%")
                )
            if conditions:
                stmt = stmt.where(and_(*conditions))
        
        if pagination:
            stmt = stmt.offset(pagination.offset).limit(pagination.limit)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def count_logs(self, filters: Optional[LogFilters] = None) -> int:
        stmt = select(func.count(LogModel.id))
        
        if filters:
            conditions = []
            if filters.level:
                conditions.append(LogModel.level == filters.level)
            if filters.module:
                conditions.append(LogModel.module == filters.module)
            if filters.start_time:
                conditions.append(LogModel.timestamp >= filters.start_time)
            if filters.end_time:
                conditions.append(LogModel.timestamp <= filters.end_time)
            if filters.correlation_id:
                conditions.append(
                    LogModel.context_json.op('->>')('correlation_id') == filters.correlation_id
                )
            if filters.search_query:
                conditions.append(
                    LogModel.message.ilike(f"%{filters.search_query}%")
                )
            if conditions:
                stmt = stmt.where(and_(*conditions))
        
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_log_stats(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        conditions = []
        if start_time:
            conditions.append(LogModel.timestamp >= start_time)
        if end_time:
            conditions.append(LogModel.timestamp <= end_time)
        
        # Total count
        total_stmt = select(func.count(LogModel.id))
        if conditions:
            total_stmt = total_stmt.where(and_(*conditions))
        total_result = await self._session.execute(total_stmt)
        total = total_result.scalar() or 0
        
        # By level
        level_stmt = select(LogModel.level, func.count(LogModel.id)).group_by(LogModel.level)
        if conditions:
            level_stmt = level_stmt.where(and_(*conditions))
        level_result = await self._session.execute(level_stmt)
        by_level = {row.level: row[1] for row in level_result.all()}
        
        # By module (top 10)
        module_stmt = (
            select(LogModel.module, func.count(LogModel.id))
            .group_by(LogModel.module)
            .order_by(desc(func.count(LogModel.id)))
            .limit(10)
        )
        if conditions:
            module_stmt = module_stmt.where(and_(*conditions))
        module_result = await self._session.execute(module_stmt)
        by_module = {row.module: row[1] for row in module_result.all()}
        
        return {
            "total": total,
            "by_level": by_level,
            "by_module": by_module,
        }

    async def search_logs(
        self,
        query: str,
        filters: Optional[LogFilters] = None,
        pagination: Optional[Pagination] = None,
    ) -> List[Log]:
        search_filters = filters or LogFilters()
        search_filters.search_query = query
        return await self.get_logs(filters=search_filters, pagination=pagination)