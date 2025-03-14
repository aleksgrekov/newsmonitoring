from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from analysis_service.src.logger.logger_config import configure_logging
from analysis_service.src.models.news_model import News
from analysis_service.src.database.service import session_factory

logger = configure_logging(__name__)


class NewsRepository:

    @staticmethod
    async def text_analysis():
        print("ok")

    @staticmethod
    async def _get_all_news() -> None:
        async with session_factory() as session:
            news_list = await session.execute(select(News))
            for news in news_list:
                logger.info(f"{news}")

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
