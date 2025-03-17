import aiohttp

from news_system.src.configs.parser_config import parser_settings
from news_system.src.logger.logger_config import configure_logging
from news_system.src.parser.interfaces import (
    IArticleParser,
    IHttpRequester,
    INewsParser,
)
from news_system.src.schemas.news_schemas import NewsResponseSchema, NewsSchema
from sqlalchemy.ext.asyncio import AsyncSession
from news_system.src.repositories.last_modified_repository import LastModifiedRepository

logger = configure_logging(__name__)


class CNNParser(INewsParser):
    def __init__(
        self,
        session: AsyncSession,
        http_requester: "IHttpRequester",
        article_parser: "IArticleParser",
    ):
        self.__url = parser_settings.NEWS_URL
        self.__session = session
        self.__http_requester = http_requester
        self.__article_parser = article_parser

    async def collect_news(self) -> NewsResponseSchema:
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(300)
            ) as client:
                logger.info(f"Парсинг страницы: {self.__url} - Начало задачи...")
                last_modified_value = await LastModifiedRepository.get_header(
                    self.__session
                )

                modified_header = await self.__http_requester.fetch_and_compare(
                    client, last_modified_value
                )
                html_content = await self.__http_requester.send_request(
                    client, modified_header
                )
                if html_content is None:
                    return NewsResponseSchema(header=modified_header, news=[])

                news_list = await self.__article_parser.parse_page(client, html_content)

                validated_news = []
                for item in news_list:
                    try:
                        validated_news.append(NewsSchema(**item))
                    except Exception as e:
                        logger.error(f"Ошибка валидации новости: {e}")

                logger.info(f"Парсинг страницы: {self.__url} - Успешно завершено!")
                await LastModifiedRepository.update_header(
                    self.__session, modified_header
                )
                return NewsResponseSchema(header=modified_header, news=validated_news)

        except Exception as e:
            logger.error(f"Ошибка при сборе новостей: {e}")
            return NewsResponseSchema(header=None, news=[])
