from typing import Optional

from src.text_analyzer.keyword_extractor import KeywordExtractor
from src.text_analyzer.sentiment_analyzer import SentimentAnalyzer
from src.text_analyzer.text_analyzer import TextAnalyzer
from src.text_analyzer.text_preprocessor import TextPreprocessor

from src.logger.logger_config import configure_logging

logger = configure_logging(__name__)


class AnalyzerFactory:
    """Фабрика для создания экземпляров TextAnalyzer и его зависимостей."""

    @staticmethod
    def create_text_analyzer(max_keywords: Optional[int] = None) -> TextAnalyzer:
        """
        Создает экземпляр TextAnalyzer с настраиваемыми параметрами.

        Args:
            max_keywords (Optional[int]): Максимальное количество ключевых слов.
                                          Если не указано, используется значение по умолчанию.

        Returns:
            TextAnalyzer: Экземпляр TextAnalyzer.
        """
        preprocessor = TextPreprocessor()
        sentiment_analyzer = SentimentAnalyzer()
        keyword_extractor = KeywordExtractor(max_keywords=max_keywords)

        text_analyzer = TextAnalyzer(
            preprocessor, sentiment_analyzer, keyword_extractor
        )
        return text_analyzer
