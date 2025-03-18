from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from news_system.src.configs.db_config import db_settings

DB_URL: str = db_settings.db_url(driver="asyncpg")
engine = create_async_engine(DB_URL)

session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Асинхронный генератор сессии базы данных.

    Используется в качестве зависимости в обработчиках FastAPI.

    Yields:
        AsyncSession: Асинхронная сессия базы данных.
    """
    async with session_factory() as session:
        yield session


# Аннотированный тип для внедрения зависимостей FastAPI
DBSession = Annotated[AsyncSession, Depends(get_session)]
