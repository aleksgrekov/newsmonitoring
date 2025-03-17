from googletrans import Translator

from database import News

from translate_service.src.schemas.translation_schemas import TranslatedNewsSchema


class TranslationService:
    """
    Сервис для перевода новостей и их заголовков.
    """

    def __init__(self):
        self._translator = Translator()

    async def translate_news(
        self, news: "News", dest_language: str = "ru"
    ) -> TranslatedNewsSchema | None:
        """
        Переводит заголовок и текст новости на указанный язык.

        :param news: Новость для перевода.
        :param dest_language: Язык, на который нужно перевести (по умолчанию "ru" — русский).
        :return: Словарь с переведенными заголовком и текстом.
        """
        try:
            translated_title = (
                await self._translator.translate(news.title, dest=dest_language)
            ).text

            translated_content = (
                await self._translator.translate(news.content, dest=dest_language)
            ).text

            return TranslatedNewsSchema(
                news_id=news.id, title=translated_title, content=translated_content
            )

        except Exception as e:
            print(f"Ошибка при переводе новости с ID {news.id}: {e}")
            return None
