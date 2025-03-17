from typing import Sequence

from sqlalchemy import select, exists
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from analysis_service.src.logger.logger_config import configure_logging
from database import News, Translation
from translate_service.src.translator.translator import TranslationService

from translate_service.src.db.service import session_factory

logger = configure_logging(__name__)


class TranslatorRepository:
    """Репозиторий для работы с новостями и их анализом."""

    @classmethod
    async def translate(cls) -> None:
        async with session_factory() as session:
            news_list = await cls._get_untranslated_news(session)

            translated_news = [
                await TranslationService.translate_news(article)
                for article in news_list
            ]

            session.add_all(
                [Translation(**translate.model_dump()) for translate in translated_news]
            )
            await cls._secure_commit(session)

    @classmethod
    async def _get_untranslated_news(cls, session: AsyncSession) -> Sequence[News]:
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
