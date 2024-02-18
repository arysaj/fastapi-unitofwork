from typing import TypeVar, Generic, Optional
from abc import ABC, abstractmethod

from src.fastapi_unitofwork.models.basemodel import BaseModel


T = TypeVar("T", bound=BaseModel)


class GenericRepository(Generic[T], ABC):
    @abstractmethod
    async def get_by_id(self, model_id: int) -> T | None:
        raise NotImplementedError()

    @abstractmethod
    async def list(self, **filters) -> list[T]:
        raise NotImplementedError()

    @abstractmethod
    async def add(self, record: T) -> T:
        raise NotImplementedError()

    @abstractmethod
    async def update(self, record: T) -> T:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, model_id: int) -> None:
        raise NotImplementedError
