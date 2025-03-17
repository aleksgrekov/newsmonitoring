from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from analysis_service.src.logger.logger_config import configure_logging
from database import NewsAnalysis, News
from analysis_service.src.db.service import session_factory
from src.text_analyzer.word_processor import analyze_text
from src.schemas.analysis_schema import NewsAnalysisCreate

logger = configure_logging(__name__)


class NewsRepository:
    """Репозиторий для работы с новостями и их анализом."""

    @classmethod
    async def text_analysis(cls) -> None:
        """Анализирует все новости и сохраняет результаты в базе данных."""
        async with session_factory() as session:
            news_list = await cls._get_all_news(session)

            analyzed_news = [
                NewsAnalysis(
                    **NewsAnalysisCreate(
                        sentiment=sentiment,
                        keywords=", ".join(keywords),
                        news_id=news_item.id,
                    ).model_dump()
                )
                for news_item in news_list
                if (text := news_item.content or news_item.title)
                and (sentiment := analyze_text(text)[0])
                and (keywords := analyze_text(text)[1])
            ]

            session.add_all(analyzed_news)
            await cls._secure_commit(session)

    @classmethod
    async def _get_all_news(cls, session: AsyncSession) -> Sequence[News]:
        """Получает все новости из базы данных."""
        result = await session.execute(select(News))
        return result.scalars().all()

    @classmethod
    async def _secure_commit(cls, session: AsyncSession) -> None:
        """Безопасно выполняет коммит в базу данных."""
        try:
            await session.commit()
        except IntegrityError as exc:
            logger.error("Ошибка целостности данных: %s", exc)
            await session.rollback()
