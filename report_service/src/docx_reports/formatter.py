from docx import Document

from database import News


class NewsFormatter:
    """Форматирует новости для вставки в отчет."""

    @staticmethod
    def format_translation(news: News, doc: Document) -> None:
        """Добавляет перевод новости в документ."""
        if news.translations and news.translations[0].title:
            paragraph = doc.add_paragraph()
            run = paragraph.add_run("Перевод: ")
            run.bold = True
            paragraph.add_run(news.translations[0].title)

        if news.translations and news.translations[0].content:
            paragraph = doc.add_paragraph()
            run = paragraph.add_run("Перевод: ")
            run.bold = True
            paragraph.add_run(news.translations[0].content)

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
            run = paragraph.add_run("Эмоциональный тон: ")
            run.bold = True
            paragraph.add_run(sentiment_text)

            if analysis.keywords:
                paragraph = doc.add_paragraph()
                run = paragraph.add_run("Ключевые слова: ")
                run.bold = True
                paragraph.add_run(analysis.keywords)
