import asyncio
import traceback
from typing import Dict, List, Optional

import aiohttp
from aiohttp import ClientSession
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from src.configs.parser_config import parser_settings
from src.logger.logger_config import configure_logging
from src.parser.interfaces import (
    IArticleParser,
    IHttpRequester,
    INewsParser,
)
from src.repositories.last_modified_repository import LastModifiedRepository
from src.schemas.news_schemas import NewsResponseSchema, NewsSchema

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

        Args:
            session (AsyncSession):
            Асинхронная сессия SQLAlchemy.

            http_requester (IHttpRequester):
            Объект для выполнения HTTP-запросов.

            article_parser (IArticleParser):
            Парсер для извлечения данных о статьях.

            last_modified_repository (LastModifiedRepository):
            Репозиторий для работы с Last-Modified.
        """
        self.__url = parser_settings.NEWS_URL
        self.__session = session
        self.__http_requester = http_requester
        self.__article_parser = article_parser
        self.__last_modified_repository = last_modified_repository

    async def collect_news(self) -> NewsResponseSchema:
        """
        Собирает новости с CNN.

        Returns:
            NewsResponseSchema: Объект с данными о новостях.
        """
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(300)
            ) as client:
                logger.info(
                    "Парсинг страницы: %s - Начало задачи...",
                    self.__url,
                )

                modified_header = await self.__get_modified_header(client)

                html_content = await self.__http_requester.send_request(
                    client, modified_header
                )
                if html_content is None:
                    logger.info(
                        "Парсинг страницы: %s - Нет новых данных.",
                        self.__url,
                    )

                    return NewsResponseSchema(header=modified_header, news=[])

                news_list = await self.__article_parser.parse_page(
                    client,
                    html_content,
                )

                validated_news = self.__validate_news(news_list)

                logger.info(
                    "Парсинг страницы: %s - Успешно завершено!",
                    self.__url,
                )

                await self.__update_last_modified(modified_header)

                return NewsResponseSchema(
                    header=modified_header,
                    news=validated_news,
                )
        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
            UnicodeDecodeError,
        ) as exc:
            logger.error(
                "Ошибка при сборе новостей: %s\n%s",
                exc,
                traceback.format_exc(),
            )
            return NewsResponseSchema(header=None, news=[])

    async def __get_modified_header(
        self,
        client: ClientSession,
    ) -> Optional[str]:
        """
        Получает заголовок Last-Modified.

        Args:
            client (ClientSession): Асинхронная HTTP-сессия.

        Returns:
            Optional[str]: Заголовок Last-Modified или None.
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

        Args:
            news_list (List[Dict[str, str]]):
            Список словарей с данными о новостях.

        Returns:
            List[NewsSchema]: Список валидированных объектов NewsSchema.
        """
        validated_news = []
        try:
            validated_news = TypeAdapter(
                List[NewsSchema],
            ).validate_python(news_list)

        except ValidationError as exc:
            logger.error(
                "Ошибка валидации новостей: %s\n%s}",
                exc,
                traceback.format_exc(),
            )
        return validated_news

    async def __update_last_modified(self, modified_header: Optional[str]):
        """
        Обновляет значение Last-Modified в базе данных.

        Args:
            modified_header (Optional[str]):
            Новое значение заголовка Last-Modified.
        """
        await self.__last_modified_repository.update_header(
            self.__session, modified_header
        )
