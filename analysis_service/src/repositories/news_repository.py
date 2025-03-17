from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from analysis_service.src.logger.logger_config import configure_logging
from database import News
from analysis_service.src.db.service import session_factory
from src.text_analyzer.word_processor import analyze_text

logger = configure_logging(__name__)


class NewsRepository:

    @classmethod
    async def text_analysis(cls):
        async with session_factory() as session:
            news = await cls._get_all_news(session)
            for one_news in news:
                content = one_news.content
                text = content if content else one_news.title
                sentiment, keywords = analyze_text(text)
                print(f"id={one_news.id}\n\t{sentiment=}\n\t\t{keywords=}")

    @staticmethod
    async def _get_all_news(session: AsyncSession) -> Sequence["News"]:
        request = await session.execute(select(News))
        return request.scalars().all()

    @staticmethod
    async def _secure_commit(session: AsyncSession) -> None:
        """
        Безопасно выполняет commit в базу данных.

        :param session: Асинхронная сессия SQLAlchemy.
        :raises IntegrityViolationException: Если возникает ошибка целостности данных.
        """
        try:
            await session.commit()
        except IntegrityError as exc:
            logger.info(exc)  # Обработка ошибок целостности
            await session.rollback()
