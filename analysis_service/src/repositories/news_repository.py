import asyncio
from typing import Sequence

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from analysis_service.src.db.service import session_factory
from analysis_service.src.logger.logger_config import configure_logging
from analysis_service.src.text_analyzer.word_processor import analyze_text
from database import News, NewsAnalysis

logger = configure_logging(__name__)


class NewsRepository:
    """Репозиторий для работы с новостями и их анализом."""

    @classmethod
    async def text_analysis(cls) -> None:
        """Анализирует все новости и сохраняет результаты в базе данных."""
        async with session_factory() as session:
            news_list = await cls._get_unanalyzed_news(session)
            analyzed_news = [
                NewsAnalysis(
                    sentiment=analysis_result[0],
                    keywords=", ".join(analysis_result[1]),
                    news_id=news_item.id,
                )
                for news_item in news_list
                if (text := news_item.content or news_item.title)
                and (analysis_result := analyze_text(text))
            ]
            if analyzed_news:
                session.add_all(analyzed_news)
                await cls._secure_commit(session)

    @classmethod
    async def _get_unanalyzed_news(cls, session: AsyncSession) -> Sequence[News]:
        """Получает новости, для которых еще нет записей в таблице NewsAnalysis."""
        stmt = select(News).where(~exists().where(NewsAnalysis.news_id == News.id))
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


news_repository = NewsRepository()
asyncio.run(news_repository.text_analysis())
