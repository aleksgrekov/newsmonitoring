from pathlib import Path
from typing import Sequence
import asyncio

from database import News
from docx import Document


class ReportGenerator:

    @staticmethod
    def generate_report(news_data: Sequence[News]) -> Document:
        doc = Document()
        doc.add_heading("Отчет по новостям", level=1)

        for news in news_data:
            doc.add_heading(news.title, level=2)

            # Добавляем перевод заголовка, если он есть
            if news.translations and news.translations[0].title:
                paragraph = doc.add_paragraph()
                run = paragraph.add_run("Перевод: ")
                run.bold = True
                paragraph.add_run(news.translations[0].title)

            # Добавляем контент новости, если он есть
            if news.content:
                doc.add_paragraph(str(news.content))

            # Добавляем перевод контента, если он есть
            if news.translations and news.translations[0].content:
                paragraph = doc.add_paragraph()
                run = paragraph.add_run("Перевод: ")
                run.bold = True
                paragraph.add_run(news.translations[0].content)

            # Анализ новости
            if news.analysis:
                analysis = news.analysis[0]
                sentiment_text = "нейтральный"
                if analysis.sentiment > 0:
                    sentiment_text = "положительный"
                elif analysis.sentiment < 0:
                    sentiment_text = "отрицательный"

                paragraph = doc.add_paragraph()
                run = paragraph.add_run("Эмоциональный тон: ")
                run.bold = True
                paragraph.add_run(sentiment_text)

                if analysis.keywords:
                    paragraph = doc.add_paragraph()
                    run = paragraph.add_run("Ключевые слова: ")
                    run.bold = True
                    paragraph.add_run(analysis.keywords)

            doc.add_paragraph("—" * 50)

        return doc

    @classmethod
    async def create_report(
        cls, news_data: Sequence[News], filename: str = "news_report.docx"
    ) -> str:
        report_folder = Path(__file__).resolve().parent / "reports"
        report_folder.mkdir(parents=True, exist_ok=True)

        path_for_save = report_folder / filename

        doc = cls.generate_report(news_data)

        await asyncio.to_thread(doc.save, path_for_save)

        return str(path_for_save)
