from datetime import datetime
from typing import Sequence

from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.db.service import session_factory
from src.docx_reports.email_sender import EmailSender
from src.docx_reports.formatter import NewsFormatter
from src.docx_reports.generator import ReportGenerator
from src.handlers.custom_exceptions import BaseCustomException
from src.logger.logger_config import configure_logging
from src.models.news_model import News
from src.schemas.report_schemas import EmailSchema

logger = configure_logging(__name__)


class ReportRepository:
    """
    Репозиторий для генерации отчетов и отправки их по email.

    Содержит методы для создания отчетов на основе данных новостей
    и отправки их на указанный адрес электронной почты.
    """

    formatter = NewsFormatter()
    report_generator = ReportGenerator(formatter)
    email_sender = EmailSender()

    @classmethod
    async def create_report_and_send_to_email(cls, email: EmailSchema) -> None:
        """
        Генерирует отчет и отправляет его на указанный email.

        Args:
            email (EmailSchema): Email пользователя,
            для отправки отчета по электронной почте.
        """
        await cls.generate_report()
        await cls.send_report_by_email(email.email)

    @classmethod
    async def generate_report(cls) -> None:
        """
        Генерирует отчет на основе данных из базы данных
        и сохраняет его в файл.
        """
        try:
            async with session_factory() as session:
                news_data = await cls._fetch_news_data(session)

                if not news_data:
                    logger.warning("Нет данных для формирования отчета.")
                    return None

                rep_path = await cls.report_generator.create_report(news_data)
                logger.info("Отчет сформирован и сохранен в %s", rep_path)

        except SQLAlchemyError as exc:
            message = ("Ошибка при генерации отчета: %s", exc)
            logger.error(message, exc_info=True)
            raise BaseCustomException(message) from exc

    @classmethod
    async def send_report_by_email(cls, email: str) -> None:
        """
        Отправляет сгенерированный отчет на указанный email.

        Args:
            email (str): Адрес электронной почты для отправки отчета.
        """

        await cls.email_sender.send_report_by_email(email)
        logger.info("Отчет успешно отправлен на email: %s", email)

    @staticmethod
    async def _fetch_news_data(session: AsyncSession) -> Sequence["News"]:
        """
        Получает данные новостей из базы данных за сегодняшний день,
        отсортированные по убыванию даты публикации.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.

        Returns:
            Sequence[News]: Список объектов новостей.
        """

        today = datetime.now().date()

        stmt = (
            select(News)
            .options(
                selectinload(News.translations),
                selectinload(News.analysis),
            )
            .filter(News.pub_date >= today)
            .order_by(desc(News.pub_date))
        )

        request = await session.execute(stmt)
        return request.scalars().all()
