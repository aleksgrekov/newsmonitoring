from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.handlers.custom_exceptions import IntegrityViolationException
from src.models.news_model import News
from src.parser.parser_factory import ParserFactory
from src.logger.logger_config import configure_logging

logger = configure_logging(__name__)


class NewsRepository:

    @classmethod
    async def add_all_news_from_parser(cls, session: AsyncSession) -> None:
        parser = ParserFactory.create_cnn_parser()
        news = await parser.collect_news()
        if not news:
            return

        stmt = insert(News).values([dict(data) for data in news])
        stmt = stmt.on_conflict_do_update(
            index_elements=["url"],
            set_={"content": stmt.excluded.content, "pub_date": stmt.excluded.pub_date},
        )
        # stmt = stmt.on_conflict_do_nothing()
        await session.execute(stmt)
        await cls._secure_commit(session)
        logger.info("В базу добавлено {} новостей!".format(len(news)))

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
