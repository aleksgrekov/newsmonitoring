from typing import List, Tuple

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from textblob import TextBlob

# Загружаем стоп-слова и лемматизатор
nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")
nltk.download("wordnet")

# Инициализируем вспомогательные объекты
STOP_WORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()


def preprocess_text(text: str) -> str:
    """Очищает и нормализует текст."""
    words = word_tokenize(text.lower())  # Приводим к нижнему регистру и токенизируем
    words = [
        word for word in words if word.isalnum() and word not in STOP_WORDS
    ]  # Убираем знаки препинания и стоп-слова
    words = [LEMMATIZER.lemmatize(word) for word in words]  # Лемматизируем
    return " ".join(words)


def analyze_text(text: str) -> Tuple[float, List[str]]:
    """Анализирует текст, возвращая тональность и ключевые слова."""
    processed_text = preprocess_text(text)
    blob = TextBlob(processed_text)

    sentiment = blob.sentiment.polarity  # [-1, 1] (негативный, нейтральный, позитивный)
    keywords = sorted(set(processed_text.split()), key=len, reverse=True)[
        :10
    ]  # Берем 10 самых длинных слов

    return sentiment, keywords
