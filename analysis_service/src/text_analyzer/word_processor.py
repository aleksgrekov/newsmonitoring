from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
from textblob import TextBlob

# Загружаем стоп-слова и лемматизатор
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()


# Функция очистки текста
def preprocess_text(text):
    words = word_tokenize(text.lower())  # Токенизация + приведение к нижнему регистру
    words = [word for word in words if word.isalnum()]  # Убираем знаки препинания
    words = [word for word in words if word not in stop_words]  # Убираем стоп-слова
    words = [lemmatizer.lemmatize(word) for word in words]  # Лемматизация
    return " ".join(words)  # Возвращаем обработанный текст


# Функция анализа текста
def analyze_text(text):
    processed_text = preprocess_text(text)
    blob = TextBlob(processed_text)

    sentiment = (
        blob.sentiment.polarity
    )  # Тональность текста (-1 -> негатив, 0 -> нейтральный, 1 -> позитив)
    keywords = list(set(processed_text.split()))[:10]

    return sentiment, keywords
