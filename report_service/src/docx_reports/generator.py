import asyncio
from pathlib import Path
from typing import Optional, Sequence

from docx import Document

from src.models.news_model import News
from src.docx_reports.formatter import NewsFormatter
from src.logger.logger_config import configure_logging

logger = configure_logging(__name__)


class ReportGenerator:
    """Генерирует отчет по новостям."""

    def __init__(self, formatter: NewsFormatter) -> None:
        self.formatter = formatter

    @staticmethod
    def _create_document() -> Document:
        """Создает новый документ с заголовком отчета."""
        doc = Document()
        doc.add_heading("Отчет по новостям", level=1)
        return doc

    def _add_news_to_document(self, doc: Document, news: News) -> None:
        """Добавляет новость в документ."""
        doc.add_heading(news.title, level=2)
        self.formatter.format_translation(news, doc)

        if news.content:
            doc.add_paragraph(str(news.content))

        self.formatter.format_analysis(news, doc)
        doc.add_paragraph("—" * 50)

    def generate_report(self, news_data: Sequence[News]) -> Document:
        """Создает отчет по переданным новостям."""
        doc = self._create_document()

        for news in news_data:
            self._add_news_to_document(doc, news)

        return doc

    async def create_report(
        self,
        news_data: Sequence[News],
        filename: str = "news_report.docx",
        output_dir: Optional[str] = None,
    ) -> str:
        """
        Создает и сохраняет отчет в файл.

        Args:
            news_data: Список новостей для отчета.
            filename: Имя файла для сохранения.
            output_dir: Директория для сохранения файла. Если не указана, используется папка 'reports'.

        Returns:
            Путь к сохраненному файлу.
        """
        # Определяем директорию для сохранения
        if output_dir:
            report_folder = Path(output_dir)
        else:
            report_folder = Path(__file__).resolve().parent / "reports"

        # Создаем директорию, если она не существует
        report_folder.mkdir(parents=True, exist_ok=True)

        # Полный путь для сохранения файла
        file = filename if filename else "news_report"
        path_for_save = report_folder / f"{file}.docx"

        # Генерируем отчет
        doc = self.generate_report(news_data)

        await asyncio.to_thread(doc.save, path_for_save)

        return str(path_for_save)

    @staticmethod
    async def send_report_by_email(
        email: str,
    ) -> str:
        """
        Имитация отправки отчета на почту.

        Args:
            email: Email адрес для отправки.
        Returns:
            Сообщение об успешной отправке.
        """

        logger.info(f"Имитация отправки отчета на email: {email}")

        return f"Отчет отправлен на email: {email}"
