from typing import Sequence, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import News
from report_service.src.db.service import session_factory
from report_service.src.docx_reports.formatter import NewsFormatter
from report_service.src.docx_reports.generator import ReportGenerator
from report_service.src.logger.logger_config import configure_logging
from report_service.src.schemas.report_schemas import ReportRequestBodySchema

logger = configure_logging(__name__)


class ReportRepository:
    """
    Репозиторий для генерации отчетов и отправки их по email.

    Содержит методы для создания отчетов на основе данных новостей и отправки их на указанный адрес электронной почты.
    """

    formatter = NewsFormatter()
    report_generator = ReportGenerator(formatter)

    @classmethod
    async def generate_report_and_send_to_email(
        cls, request_body: ReportRequestBodySchema
    ) -> None:
        """
        Генерирует отчет и отправляет его на указанный email.

        Args:
            request_body (ReportRequestBodySchema): Данные для генерации отчета и отправки на email.
        """
        await cls.generate_report(request_body.filename, request_body.output_dir)
        await cls.send_report_by_email(request_body.email)

    @classmethod
    async def generate_report(
        cls,
        filename: str = "news_report.docx",
        output_dir: Optional[str] = None,
    ) -> None:
        """
        Генерирует отчет на основе данных из базы данных и сохраняет его в файл.

        Args:
            filename (str): Имя файла для сохранения отчета. По умолчанию "news_report.docx".
            output_dir (Optional[str]): Директория для сохранения отчета. Если не указана, используется папка 'reports'.
        """
        try:
            async with session_factory() as session:
                news_data = await cls._fetch_news_data(session)

                if not news_data:
                    logger.warning("Нет данных для формирования отчета.")
                    return None

                # Генерация и сохранение отчета
                report_path = await cls.report_generator.create_report(
                    news_data, filename, output_dir
                )
                logger.info("Отчет сформирован и сохранен в %s", report_path)

        except Exception as e:
            logger.error("Ошибка при генерации отчета: %s", e, exc_info=True)
            return None

    @classmethod
    async def send_report_by_email(
        cls,
        email: str,
    ) -> None:
        """
        Отправляет сгенерированный отчет на указанный email.

        Args:
            email (str): Адрес электронной почты для отправки отчета.
        """
        try:
            # Имитация отправки отчета на почту
            await cls.report_generator.send_report_by_email(email)
            logger.info("Отчет успешно отправлен на email: %s", email)
        except Exception as e:
            logger.error("Ошибка при отправке отчета на email: %s", e, exc_info=True)

    @staticmethod
    async def _fetch_news_data(session: AsyncSession) -> Sequence["News"]:
        """
        Получает данные новостей из базы данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.

        Returns:
            Sequence[News]: Список объектов новостей.
        """
        stmt = select(News).options(
            selectinload(News.translations), selectinload(News.analysis)
        )
        request = await session.execute(stmt)
        return request.scalars().all()
