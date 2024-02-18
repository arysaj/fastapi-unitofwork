from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.fastapi_unitofwork.configs.settings import get_settings

settings = get_settings()

async_engine = create_async_engine(settings.DATABASE_URL, echo=True)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async_session_maker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session
