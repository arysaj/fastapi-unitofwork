from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated

from src.fastapi_unitofwork.repositories.user import UserRepositoryBase, UserRepository
from src.fastapi_unitofwork.configs.database import get_async_session


class UnitOfWorkBase(ABC):
    users: UserRepositoryBase

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rollback()

    @abstractmethod
    async def commit(self):
        raise NotImplementedError()

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError()


class UnitOfWork(UnitOfWorkBase):
    def __init__(
        self, session_factory: Annotated[AsyncSession, Depends(get_async_session)]
    ) -> None:
        self._session_factory = session_factory

    async def __aenter__(self):
        self._session = self._session_factory
        self.users = UserRepository(self._session)
        return super().__aenter__()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
