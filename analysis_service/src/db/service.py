from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.configs.db_config import db_settings

# Создаем асинхронный движок базы данных
DB_URL: str = db_settings.db_url(driver="asyncpg")
engine = create_async_engine(DB_URL)

# Фабрика сессий для API
session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Асинхронный генератор сессии базы данных.

    Yields:
        AsyncSession: Асинхронная сессия базы данных.
    """
    async with session_factory() as session:
        yield session
