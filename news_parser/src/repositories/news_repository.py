from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.handlers.custom_exceptions import IntegrityViolationException
from src.logger.logger_config import configure_logging
from src.models.news_model import News
from src.parser.parser_factory import ParserFactory
from src.rabbit.publisher import publisher
from src.schemas.base_schemas import SuccessResponse

logger = configure_logging(__name__)


class NewsRepository:
    """
    Репозиторий для работы с новостями.

    Методы:
        - add_all_news_from_parser: Добавляет новости,
        полученные от парсера, в базу данных.
        - _secure_commit: Безопасно выполняет commit.
    """

    @classmethod
    async def add_all_news_from_parser(cls, session: AsyncSession) -> None:
        """
        Добавляет новости, полученные от парсера, в базу данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
        """
        parser = ParserFactory.create_cnn_parser(session)
        news_data = await parser.collect_news()
        news = news_data.news

        if not news:
            logger.info("Нет новых новостей для добавления.")
            return

        start_count = await cls._get_news_count(session)

        await cls._insert_news(session, news)

        end_count = await cls._get_news_count(session)
        added_news_count = end_count - start_count

        await cls._secure_commit(session)
        logger.info("В базу добавлено %s новостей!", added_news_count)
        message = SuccessResponse(message=news_data.header)
        await publisher.send_messages(message.model_dump_json())

    @staticmethod
    async def _get_news_count(session: AsyncSession) -> int:
        """
        Получает текущее количество новостей в базе данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.

        Returns:
            int: Количество новостей.
        """
        result = await session.execute(func.count(News.id))
        count = result.scalar()
        return count if count is not None else 0

    @staticmethod
    async def _insert_news(session: AsyncSession, news: list) -> None:
        """
        Вставляет новости в базу данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            news (list): Список новостей для вставки.
        """
        stmt = insert(News).values([data.model_dump() for data in news])
        stmt = stmt.on_conflict_do_nothing()
        await session.execute(stmt)

    @staticmethod
    async def _secure_commit(session: AsyncSession) -> None:
        """
        Безопасно выполняет commit в базу данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.

        Raises:
            IntegrityViolationException:
            Если возникает ошибка целостности данных.
        """
        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise IntegrityViolationException(str(exc))
