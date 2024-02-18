from abc import ABC
from typing import Any, Sequence

from sqlalchemy import select, Select, and_, Row
from sqlalchemy.ext.asyncio import AsyncSession

from src.fastapi_unitofwork.repositories.generic import GenericRepository, T


class GenericSqlRepository(GenericRepository[T], ABC):
    def __init__(self, session: AsyncSession, model_cls: [T]) -> None:
        self._session = session
        self._model_cls = model_cls

    def _construct_get_stmt(self, model_id: int) -> Select[tuple[Any]] | Select[Any]:
        stmt = select(self._model_cls).where(self._model_cls.id == model_id)
        return stmt

    async def get_by_id(self, model_id: int) -> T | None:
        stmt = self._construct_get_stmt(model_id)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    def _construct_list_stmt(self, **filters) -> Select[tuple[Any] | Select[Any]]:
        stmt = select(self._model_cls)
        where_clauses = []
        for c, v in filters.items():
            if not hasattr(self._model_cls, c):
                raise ValueError(f"Invalid column name {c}")
            where_clauses.append(getattr(self._model_cls, c) == v)

        if len(where_clauses) == 1:
            stmt = stmt.where(where_clauses[0])
        elif len(where_clauses) > 1:
            stmt = stmt.where(and_(*where_clauses))
        return stmt

    async def list(self, **filters) -> Sequence[Row[tuple[Any] | Select[Any]]]:
        stmt = self._construct_list_stmt(**filters)
        res = await self._session.execute(stmt)
        return res.scalars().all()

    async def add(self, record: T) -> T:
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record

    async def update(self, record: T) -> T:
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record

    async def delete(self, model_id: int) -> None:
        record = self.get_by_id(model_id)
        if record is not None:
            await self._session.delete(record)
            await self._session.flush()
