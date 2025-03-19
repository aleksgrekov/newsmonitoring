from abc import ABC, abstractmethod
from typing import List


class ITextPreprocessor(ABC):
    """Абстрактный класс для предварительной обработки текста."""

    @abstractmethod
    def preprocess(self, text: str) -> str:
        """
        Очищает и нормализует текст.

        Args:
            text (str): Исходный текст для обработки.

        Returns:
            str: Очищенный и нормализованный текст.
        """
        pass


class ISentimentAnalyzer(ABC):
    """Абстрактный класс для анализа тональности текста."""

    @abstractmethod
    def analyze_sentiment(self, text: str) -> float:
        """
        Анализирует тональность текста.

        Args:
            text (str): Исходный текст для анализа.

        Returns:
            float: Тональность текста (от -1 до 1).
        """
        pass


class IKeywordExtractor(ABC):
    """Абстрактный класс для извлечения ключевых слов."""

    @abstractmethod
    def extract_keywords(self, text: str) -> List[str]:
        """
        Извлекает ключевые слова из текста.

        Args:
            text (str): Исходный текст для анализа.

        Returns:
            List[str]: Список ключевых слов.
        """
        pass
