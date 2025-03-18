import asyncio
from typing import Sequence

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from analysis_service.src.logger.logger_config import configure_logging
from database import News, Translation
from translate_service.src.db.service import session_factory
from translate_service.src.translator.translator import TranslationService

logger = configure_logging(__name__)


class TranslatorRepository:
    """Репозиторий для работы с переводами новостей."""

    translation_service = TranslationService()

    @classmethod
    async def translate(cls) -> None:
        """Переводит все новости, которые еще не были переведены."""
        async with session_factory() as session:
            news_list = await cls._get_untranslated_news(session)

            translated_news = await asyncio.gather(
                *(
                    cls.translation_service.translate_news(article)
                    for article in news_list
                )
            )

            translations = [
                Translation(**translate.model_dump()) for translate in translated_news
            ]
            session.add_all(translations)

            # Выполняем коммит в базу данных
            await cls._secure_commit(session)

    @classmethod
    async def _get_untranslated_news(cls, session: AsyncSession) -> Sequence[News]:
        """Получает новости, которые еще не были переведены."""
        stmt = select(News).where(~exists().where(Translation.news_id == News.id))
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def _secure_commit(cls, session: AsyncSession) -> None:
        """Безопасно выполняет коммит в базу данных."""
        try:
            await session.commit()
        except IntegrityError as exc:
            logger.error("Ошибка целостности данных: %s", exc)
            await session.rollback()


translator_repository = TranslatorRepository()
asyncio.run(translator_repository.translate())
