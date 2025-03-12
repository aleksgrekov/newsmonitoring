from typing import Dict, List

from src.configs.parser_config import parser_settings
from src.logger.logger_config import configure_logging
from src.parser.article_parser import ArticleParser
from src.parser.http_requester import HttpRequester
from src.parser.base_parser import BaseParser

logger = configure_logging(__name__)


class CNNParser(BaseParser):
    def __init__(self):
        self.__url = parser_settings.NEWS_URL
        self.__http_requester = HttpRequester()
        self.__article_parser = ArticleParser()

    async def collect_news(self) -> List[Dict[str, str]]:
        try:
            logger.info(f"Парсинг страницы: {self.__url} - Начало задачи...")
            modified_header = await self.__http_requester.fetch_and_compare()
            html_content = await self.__http_requester.send_request(modified_header)
            if html_content is None:
                return []

            news_list = await self.__article_parser.parse_page(html_content)
            logger.info(f"Парсинг страницы: {self.__url} - Успешно завершено!")
            return news_list
        except Exception as e:
            logger.error(f"Ошибка при сборе новостей: {e}")
            return []


cnn_parser = CNNParser()
