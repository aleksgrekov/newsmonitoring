from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TYPE_CHECKING

from src.handlers.custom_exceptions import IntegrityViolationException
from src.models.news_model import News

if TYPE_CHECKING:
    from src.parser.base_parser import BaseParser


class NewsRepository:

    @classmethod
    async def add_all_news_from_parser(
        cls, parser: "BaseParser", session: AsyncSession
    ):
        news = await parser.collect_news()
        if news:
            session.add_all([News(**data) for data in news])
            await cls._secure_commit(session)
        # Отправка сообщения в очередь!

    @staticmethod
    async def _secure_commit(session: AsyncSession) -> None:
        """
        Безопасно выполняет commit в базу данных.

        :param session: Асинхронная сессия SQLAlchemy.
        :raises IntegrityViolationException: Если возникает ошибка целостности данных.
        """
        try:
            await session.commit()
        except IntegrityError as exc:  # Обработка ошибок целостности
            await session.rollback()
            raise IntegrityViolationException(str(exc))
