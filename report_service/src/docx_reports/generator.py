from pathlib import Path
from typing import Sequence
import asyncio

from database import News
from docx import Document

from report_service.src.docx_reports.formatter import NewsFormatter


class ReportGenerator:
    """Генерирует отчет по новостям."""

    def __init__(self, formatter: NewsFormatter) -> None:
        self.formatter = formatter

    def generate_report(self, news_data: Sequence[News]) -> Document:
        """Создает отчет по переданным новостям."""
        doc = Document()
        doc.add_heading("Отчет по новостям", level=1)

        for news in news_data:
            doc.add_heading(news.title, level=2)

            self.formatter.format_translation(news, doc)

            if news.content:
                doc.add_paragraph(str(news.content))

            self.formatter.format_analysis(news, doc)

            doc.add_paragraph("—" * 50)

        return doc

    async def create_report(
        self, news_data: Sequence[News], filename: str = "news_report.docx"
    ) -> str:
        """Создает и сохраняет отчет в файл."""
        report_folder = Path(__file__).resolve().parent / "reports"
        report_folder.mkdir(parents=True, exist_ok=True)

        path_for_save = report_folder / filename
        doc = self.generate_report(news_data)

        await asyncio.to_thread(doc.save, path_for_save)

        return str(path_for_save)
