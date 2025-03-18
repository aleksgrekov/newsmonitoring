import traceback
from typing import List, Dict, Optional
import aiohttp
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError, parse_obj_as

from news_system.src.configs.parser_config import parser_settings
from news_system.src.logger.logger_config import configure_logging
from news_system.src.parser.interfaces import (
    IArticleParser,
    IHttpRequester,
    INewsParser,
)
from news_system.src.schemas.news_schemas import NewsResponseSchema, NewsSchema
from news_system.src.repositories.last_modified_repository import LastModifiedRepository

logger = configure_logging(__name__)


class CNNParser(INewsParser):
    """
    Парсер для сбора новостей с CNN.
    """

    def __init__(
        self,
        session: AsyncSession,
        http_requester: IHttpRequester,
        article_parser: IArticleParser,
        last_modified_repository: LastModifiedRepository,
    ):
        """
        Инициализация парсера.

        :param session: Асинхронная сессия SQLAlchemy.
        :param http_requester: Объект для выполнения HTTP-запросов.
        :param article_parser: Парсер для извлечения данных о статьях.
        :param last_modified_repository: Репозиторий для работы с Last-Modified.
        """
        self.__url = parser_settings.NEWS_URL
        self.__session = session
        self.__http_requester = http_requester
        self.__article_parser = article_parser
        self.__last_modified_repository = last_modified_repository

    async def collect_news(self) -> NewsResponseSchema:
        """
        Собирает новости с CNN.

        :return: Объект NewsResponseSchema с данными о новостях.
        """
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(300)
            ) as client:
                logger.info(f"Парсинг страницы: {self.__url} - Начало задачи...")

                modified_header = await self.__get_modified_header(client)

                html_content = await self.__http_requester.send_request(
                    client, modified_header
                )
                if html_content is None:
                    logger.info(f"Парсинг страницы: {self.__url} - Нет новых данных.")
                    return NewsResponseSchema(header=modified_header, news=[])

                news_list = await self.__article_parser.parse_page(client, html_content)
                validated_news = self.__validate_news(news_list)

                logger.info(f"Парсинг страницы: {self.__url} - Успешно завершено!")

                await self.__update_last_modified(modified_header)
                return NewsResponseSchema(header=modified_header, news=validated_news)

        except Exception as e:
            logger.error(f"Ошибка при сборе новостей: {e}\n{traceback.format_exc()}")
            return NewsResponseSchema(header=None, news=[])

    async def __get_modified_header(self, client: ClientSession) -> Optional[str]:
        """
        Получает заголовок Last-Modified.

        :param client: Асинхронная HTTP-сессия.
        :return: Заголовок Last-Modified или None.
        """
        last_modified_value = await self.__last_modified_repository.get_header(
            self.__session
        )
        return await self.__http_requester.fetch_and_compare(
            client, last_modified_value
        )

    @staticmethod
    def __validate_news(news_list: List[Dict[str, str]]) -> List[NewsSchema]:
        """
        Валидирует данные о новостях.

        :param news_list: Список словарей с данными о новостях.
        :return: Список валидированных объектов NewsSchema.
        """
        validated_news = []
        try:
            validated_news = parse_obj_as(List[NewsSchema], news_list)
        except ValidationError as e:
            logger.error(f"Ошибка валидации новостей: {e}\n{traceback.format_exc()}")
        return validated_news

    async def __update_last_modified(self, modified_header: Optional[str]):
        """
        Обновляет значение Last-Modified в базе данных.

        :param modified_header: Новое значение заголовка Last-Modified.
        """
        await self.__last_modified_repository.update_header(
            self.__session, modified_header
        )
