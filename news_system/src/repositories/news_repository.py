from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from news_system.src.handlers.custom_exceptions import IntegrityViolationException
from news_system.src.logger.logger_config import configure_logging
from news_system.src.models.news_model import News
from news_system.src.rabbit.publisher import publisher
from news_system.src.parser.parser_factory import ParserFactory

logger = configure_logging(__name__)


class NewsRepository:

    @classmethod
    async def add_all_news_from_parser(cls, session: AsyncSession) -> None:
        parser = ParserFactory.create_cnn_parser()
        news = await parser.collect_news()
        if not news:
            return

        start_count = (await session.execute(func.count(News.id))).scalar()

        stmt = insert(News).values([dict(data) for data in news])
        stmt = stmt.on_conflict_do_nothing()

        await session.execute(stmt)
        await cls._secure_commit(session)

        end_count = (await session.execute(func.count(News.id))).scalar()

        added_news_count = end_count - start_count

        message = "В базу добавлено {} новостей!".format(added_news_count)
        logger.info(message)
        await publisher.send_messages(message)

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
