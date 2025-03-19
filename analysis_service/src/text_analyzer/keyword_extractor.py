from typing import List, Optional

from src.logger.logger_config import configure_logging
from src.text_analyzer.interfaces import IKeywordExtractor

logger = configure_logging(__name__)


class KeywordExtractor(IKeywordExtractor):
    """Класс для извлечения ключевых слов."""

    def __init__(self, max_keywords: Optional[int] = 10):
        """
        Инициализирует экземпляр KeywordExtractor.

        Args:
            max_keywords (Optional[int]): Максимальное количество ключевых слов.
                                          По умолчанию 10.
        """
        self.max_keywords = max_keywords

    def extract_keywords(self, text: str) -> List[str]:
        """
        Извлекает ключевые слова из текста.

        Args:
            text (str): Исходный текст для анализа.

        Returns:
            List[str]: Список ключевых слов.
        """
        try:
            # Извлекаем уникальные слова и сортируем их по длине
            words: List[str] = sorted(set(text.split()), key=len, reverse=True)
            return words[: self.max_keywords]
        except Exception as e:
            logger.error(f"Ошибка при извлечении ключевых слов: {e}")
            raise
