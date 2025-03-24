from src.logger.logger_config import configure_logging
from src.text_analyzer.interfaces import ISentimentAnalyzer
from textblob import TextBlob

logger = configure_logging(__name__)


class SentimentAnalyzer(ISentimentAnalyzer):
    """Класс для анализа тональности текста."""

    def analyze_sentiment(self, text: str) -> float:
        """
        Анализирует тональность текста.

        Args:
            text (str): Исходный текст для анализа.

        Returns:
            float: Тональность текста (от -1 до 1).
        """
        try:
            blob: TextBlob = TextBlob(text)
            return blob.sentiment.polarity
        except (AttributeError, TypeError) as exc:
            logger.error("Ошибка при анализе тональности текста:\n%s", exc)
            raise
