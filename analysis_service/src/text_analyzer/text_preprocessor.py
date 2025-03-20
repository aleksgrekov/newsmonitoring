from typing import List, Set

import nltk
from nltk import WordNetLemmatizer, word_tokenize
from nltk.corpus import stopwords
from src.logger.logger_config import configure_logging
from src.text_analyzer.interfaces import ITextPreprocessor

# Загружаем стоп-слова и лемматизатор
nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")
nltk.download("wordnet")

logger = configure_logging(__name__)


class TextPreprocessor(ITextPreprocessor):
    """Класс для предварительной обработки текста."""

    def __init__(self) -> None:
        self.stop_words: Set[str] = set(stopwords.words("english"))
        self.lemmatizer: WordNetLemmatizer = WordNetLemmatizer()

    def preprocess(self, text: str) -> str:
        """
        Очищает и нормализует текст.

        Args:
            text (str): Исходный текст для обработки.

        Returns:
            str: Очищенный и нормализованный текст.
        """
        try:
            # Приводим текст к нижнему регистру и токенизируем
            tokens: List[str] = word_tokenize(text.lower())

            # Убираем знаки препинания и стоп-слова
            filtered_words: List[str] = [
                word
                for word in tokens
                if word.isalnum() and word not in self.stop_words
            ]

            # Лемматизируем слова
            lemmatized_words: List[str] = [
                self.lemmatizer.lemmatize(word) for word in filtered_words
            ]
            return " ".join(lemmatized_words)
        except Exception as exc:
            logger.error(
                "Ошибка при предварительной обработке текста: %s",
                exc,
            )
            raise
