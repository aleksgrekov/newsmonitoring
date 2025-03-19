from docx import Document
from docx.text.paragraph import Paragraph

from src.models.news_model import News


class NewsFormatter:
    """Форматирует новости для вставки в отчет."""

    @staticmethod
    def _add_bold_run(paragraph: "Paragraph", text: str) -> None:
        """Добавляет жирный текст в параграф."""
        run = paragraph.add_run(text)
        run.bold = True

    @staticmethod
    def format_translation(news: News, doc: Document) -> None:
        """Добавляет перевод новости в документ."""
        if news.translations and news.translations[0]:
            translation = news.translations[0]
            if translation.title:
                paragraph = doc.add_paragraph()
                NewsFormatter._add_bold_run(paragraph, "Перевод: ")
                paragraph.add_run(translation.title)

            if translation.content:
                paragraph = doc.add_paragraph()
                NewsFormatter._add_bold_run(paragraph, "Перевод: ")
                paragraph.add_run(translation.content)

    @staticmethod
    def format_analysis(news: News, doc: Document) -> None:
        """Добавляет анализ новости в документ."""
        if news.analysis:
            analysis = news.analysis[0]
            sentiment_text = "нейтральный"
            if analysis.sentiment > 0:
                sentiment_text = "положительный"
            elif analysis.sentiment < 0:
                sentiment_text = "отрицательный"

            paragraph = doc.add_paragraph()
            NewsFormatter._add_bold_run(paragraph, "Эмоциональный тон: ")
            paragraph.add_run(sentiment_text)

            if analysis.keywords:
                paragraph = doc.add_paragraph()
                NewsFormatter._add_bold_run(paragraph, "Ключевые слова: ")
                paragraph.add_run(analysis.keywords)
