import asyncio
from typing import Sequence

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.service import session_factory
from src.logger.logger_config import configure_logging
from src.models.news_model import News
from src.models.translations_model import Translation
from src.translator.translator import TranslationService

logger = configure_logging(__name__)


class TranslatorRepository:
    """Репозиторий для работы с переводами новостей."""

    @classmethod
    async def translate(cls) -> None:
        """
        Переводит все новости, которые еще не были переведены.

        Для каждой новости, которая еще не имеет перевода,
        выполняется перевод, и результат сохраняется в базе данных.

        """
        async with session_factory() as session:
            news_list = await cls._get_untranslated_news(session)
            translation_service = await cls._get_translator()

            translated_news = await asyncio.gather(
                *(
                    translation_service.translate_news(
                        article,
                    )
                    for article in news_list
                )
            )

            translations = [
                Translation(
                    **translate.model_dump(),
                )
                for translate in translated_news
            ]
            session.add_all(translations)

            await cls._secure_commit(session)

    @staticmethod
    async def _get_translator() -> TranslationService:
        """
        Создает экземпляр сервиса перевода текстов.

        Returns:
             TranslationService: экземпляр сервиса перевода текстов.
        """
        return TranslationService()

    @classmethod
    async def _get_untranslated_news(
        cls,
        session: AsyncSession,
    ) -> Sequence[News]:
        """
        Получает новости, которые еще не были переведены.

        Выполняет запрос в базу данных,
        чтобы вернуть все новости, у которых еще нет перевода.

        Args:
            session (AsyncSession):
            Асинхронная сессия для работы с базой данных.

        Returns:
            Sequence[News]: Список объектов News, которые еще не переведены.
        """
        select_query = select(News)
        where_query = ~exists().where(Translation.news_id == News.id)
        stmt = select_query.where(where_query)

        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def _secure_commit(cls, session: AsyncSession) -> None:
        """
        Безопасно выполняет коммит в базу данных.

        Обрабатывает исключения, связанные с целостностью данных,
        и откатывает транзакцию в случае ошибок.

        Args:
            session (AsyncSession):
            Асинхронная сессия для работы с базой данных.
        """
        try:
            await session.commit()
        except IntegrityError as exc:
            logger.error("Ошибка целостности данных: %s", exc)
            await session.rollback()
