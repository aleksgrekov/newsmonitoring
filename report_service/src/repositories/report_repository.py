from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import News
from report_service.src.logger.logger_config import configure_logging
from report_service.src.db.service import session_factory
from report_service.src.docx_reports.generator import ReportGenerator
from report_service.src.docx_reports.formatter import NewsFormatter

logger = configure_logging(__name__)


class ReportRepository:
    formatter = NewsFormatter()
    report_generator = ReportGenerator(formatter)

    @classmethod
    async def generate_report(cls):
        async with session_factory() as session:
            news_data = await cls._fetch_news_data(session)

            if news_data:
                filename = await cls.report_generator.create_report(news_data)
                logger.info("Отчет сформирован и сохранен в %s", filename)

    @staticmethod
    async def _fetch_news_data(session: AsyncSession) -> Sequence["News"]:
        stmt = select(News).options(
            selectinload(News.translations), selectinload(News.analysis)
        )
        request = await session.execute(stmt)
        return request.scalars().all()
