import logging

from googletrans import Translator
from src.logger.logger_config import configure_logging
from src.models.news_model import News
from src.schemas.translation_schemas import TranslatedNewsSchema

logger = configure_logging(__name__)
logging.getLogger("_client").setLevel(logging.WARNING)  # Отключить INFO-логи


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
            TranslatedNewsSchema | None:
            Объект с переведёнными заголовком и текстом
            или None в случае ошибки.
        """
        try:
            translated_title = await self._translator.translate(
                news.title, dest=dest_language
            )
            translated_content = await self._translator.translate(
                news.content, dest=dest_language
            )

            return TranslatedNewsSchema(
                news_id=news.id,
                title=translated_title.text,
                content=translated_content.text,
            )

        except (AttributeError, ValueError, RuntimeError) as exc:
            logger.error(
                "Ошибка при переводе новости с ID %s: %s",
                news.id,
                exc,
            )
            return None
        except Exception as critical_exc:
            logger.error(
                "Непредвиденная ошибка при переводе новости с ID %s: %s",
                news.id,
                critical_exc,
                exc_info=True,
            )
            return None
