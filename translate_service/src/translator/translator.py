from googletrans import Translator
import asyncio
from database import News
from translate_service.src.schemas.translation_schemas import TranslatedNewsSchema


class TranslationService:
    """
    Сервис для перевода заголовков и текстов новостей.
    """

    def __init__(self):
        self._translator = Translator()

    async def translate_news(
        self, news: "News", dest_language: str = "ru"
    ) -> TranslatedNewsSchema | None:
        """
        Переводит заголовок и текст новости на указанный язык.

        Args:
            news (News): Новость, которую нужно перевести.
            dest_language (str): Язык перевода (по умолчанию "ru" — русский).

        Returns:
            TranslatedNewsSchema | None: Объект с переведёнными заголовком и текстом
            или None в случае ошибки.
        """
        try:
            translated_title = await asyncio.to_thread(
                self._translator.translate, news.title, src="auto", dest=dest_language
            )
            translated_content = await asyncio.to_thread(
                self._translator.translate, news.content, src="auto", dest=dest_language
            )

            return TranslatedNewsSchema(
                news_id=news.id,
                title=translated_title.text,
                content=translated_content.text,
            )

        except Exception as e:
            print(f"Ошибка при переводе новости с ID {news.id}: {e}")
            return None
