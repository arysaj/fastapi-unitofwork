from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.fastapi_unitofwork.repositories.generic import GenericRepository
from src.fastapi_unitofwork.repositories.genericsql import GenericSqlRepository
from src.fastapi_unitofwork.models.user import UserModel


class UserRepositoryBase(GenericRepository[UserModel], ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> UserModel | None:
        raise NotImplementedError()


class UserRepository(GenericSqlRepository[UserModel], UserRepositoryBase):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserModel)

    async def get_by_email(self, email: str) -> UserModel | None:
        stmt = select(self._model_cls).where(self._model_cls.email == email)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()
