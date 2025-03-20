from typing import Sequence

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.service import session_factory
from src.logger.logger_config import configure_logging
from src.models.news_analysis_model import NewsAnalysis
from src.models.news_model import News
from src.text_analyzer.analyzer_factory import AnalyzerFactory
from src.text_analyzer.text_analyzer import TextAnalyzer

logger = configure_logging(__name__)


class NewsAnalyzerRepository:
    """Репозиторий для работы с новостями и их анализом в базе данных."""

    @classmethod
    async def analyze_and_save_news(cls) -> None:
        """
        Анализирует все новые новости и сохраняет результаты в базе данных.
        """
        async with session_factory() as session:
            news_list = await cls._get_unanalyzed_news(session)
            analyzer = cls._get_analyzer()
            analyzed_news = [
                NewsAnalysis(
                    sentiment=result[0],
                    keywords=", ".join(result[1]),
                    news_id=news_item.id,
                )
                for news_item in news_list
                if (
                    result := analyzer.analyze(
                        news_item.content or news_item.title,
                    )
                )
            ]

            await cls._save_analysis_results(session, analyzed_news)

    @staticmethod
    def _get_analyzer() -> TextAnalyzer:
        """
        Создает экземпляр анализатора текста из фабрики.

        Returns:
             TextAnalyzer: экземпляр анализатора текста.
        """
        return AnalyzerFactory.create_text_analyzer()

    @staticmethod
    async def _get_unanalyzed_news(session: AsyncSession) -> Sequence[News]:
        """
        Получает список новостей, которые еще не были проанализированы.

        Args:
            session (AsyncSession): Сессия базы данных.

        Returns:
            Sequence[News]: Список необработанных новостей.
        """
        logger.info("Запрос необработанных новостей из базы данных.")

        select_query = select(News)
        where_query = ~exists().where(NewsAnalysis.news_id == News.id)
        stmt = select_query.where(where_query)

        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def _save_analysis_results(
        cls, session: AsyncSession, analyzed_news: list[NewsAnalysis]
    ) -> None:
        """
        Сохраняет результаты анализа в базу данных.

        Args:
            session (AsyncSession): Сессия базы данных.

            analyzed_news (list[NewsAnalysis]):
            Список проанализированных новостей.

        Raises:
            IntegrityError:
            Если возникает ошибка целостности данных при коммите.
        """
        if not analyzed_news:
            logger.info("Нет данных для сохранения в таблицу.")
            return

        logger.info(
            "Сохранение %d записей анализа в базу данных.",
            len(analyzed_news),
        )
        session.add_all(analyzed_news)
        await cls._secure_commit(session)

    @staticmethod
    async def _secure_commit(session: AsyncSession) -> None:
        """
        Безопасно выполняет коммит транзакции.

        Args:
            session (AsyncSession): Сессия базы данных.

        Raises:
            IntegrityError: Логирует и выбрасывает исключение при ошибке.
        """
        try:
            await session.commit()
            logger.info("Изменения успешно сохранены в базе данных.")
        except IntegrityError as exc:
            logger.error("Ошибка целостности данных при коммите: %s", exc)
            await session.rollback()
            raise
