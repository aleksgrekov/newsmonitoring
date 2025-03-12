from typing import Dict, List

from src.configs.parser_config import parser_settings
from src.logger.logger_config import configure_logging
from src.parser.article_parser import ArticleParser
from src.parser.http_requester import HttpRequester

logger = configure_logging(__name__)


class CNNParser:
    def __init__(self):
        self.__url = parser_settings.NEWS_URL
        self.__http_requester = HttpRequester()
        self.__article_parser = ArticleParser()

    def collect_news(self) -> List[Dict[str, str]]:
        logger.info(f"Парсинг страницы: {self.__url}")
        modified_header = self.__http_requester.fetch_and_compare()
        html_content = self.__http_requester.send_request(modified_header)
        if html_content is None:
            return []

        news_list = self.__article_parser.parse_page(html_content)

        return news_list


x = CNNParser()
for n in x.collect_news():
    print(n)
