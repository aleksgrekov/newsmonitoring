from typing import List, Tuple

from analysis_service.src.text_analyzer.interfaces import (
    ITextPreprocessor,
    ISentimentAnalyzer,
    IKeywordExtractor,
)
from analysis_service.src.logger.logger_config import configure_logging

logger = configure_logging(__name__)


class TextAnalyzer:
    """
    Класс для анализа текста, объединяющий предварительную обработку,
    анализ тональности и извлечение ключевых слов.
    """

    def __init__(
        self,
        text_preprocessor: ITextPreprocessor,
        sentiment_analysis_tool: ISentimentAnalyzer,
        keyword_extraction_tool: IKeywordExtractor,
    ):
        """
        Инициализирует экземпляр TextAnalyzer.

        Args:
            text_preprocessor (ITextPreprocessor): Класс для предварительной обработки текста.
            sentiment_analysis_tool (ISentimentAnalyzer): Класс для анализа тональности.
            keyword_extraction_tool (IKeywordExtractor): Класс для извлечения ключевых слов.
        """
        self.preprocessor = text_preprocessor
        self.sentiment_analyzer = sentiment_analysis_tool
        self.keyword_extractor = keyword_extraction_tool

    def analyze(self, text: str) -> Tuple[float, List[str]]:
        """
        Анализирует текст, возвращая тональность и ключевые слова.

        Args:
            text (str): Исходный текст для анализа.

        Returns:
            Tuple[float, List[str]]: Кортеж, содержащий тональность текста (от -1 до 1)
                                     и список ключевых слов.
        """
        try:
            # Предварительная обработка текста
            processed_text: str = self.preprocessor.preprocess(text)

            # Анализ тональности
            sentiment: float = self.sentiment_analyzer.analyze_sentiment(processed_text)

            # Извлечение ключевых слов
            keywords: List[str] = self.keyword_extractor.extract_keywords(
                processed_text
            )

            return sentiment, keywords
        except Exception as e:
            logger.error(f"Ошибка при анализе текста: {e}")
            raise
