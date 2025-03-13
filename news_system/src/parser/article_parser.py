import asyncio
from asyncio import Semaphore
from typing import Dict, List

from aiohttp import ClientResponseError, ClientSession, ClientTimeout
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from fake_useragent import UserAgent

from src.configs.parser_config import parser_settings
from src.logger.logger_config import configure_logging
from src.parser.interfaces import IArticleParser

logger = configure_logging(__name__)
semaphore = Semaphore(1)

MAX_RETRIES = 5  # Добавим ограничение


class ArticleParser(IArticleParser):

    async def parse_page(
        self, client: "ClientSession", html_content: bytes
    ) -> List[Dict[str, str]]:
        try:
            soup = BeautifulSoup(html_content, "lxml")
            containers = soup.select("div.card.container__item")

            tasks = [
                self.__parse_cnn_container(container, client)
                for container in containers
                if container
            ]
            results = await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )
            return [
                result
                for result in results
                if isinstance(result, dict) and bool(result)
            ]
        except Exception as e:
            logger.error(f"Ошибка при парсинге страницы: {e}")
            return []

    async def __parse_cnn_container(
        self,
        container,
        client: "ClientSession",
    ) -> Dict[str, str]:
        async with semaphore:
            try:
                headline_tag = container.find("span", class_="container__headline-text")
                title = headline_tag.text.strip() if headline_tag else "No title"

                link_tag = container.find("a", href=True)
                link = link_tag["href"] if link_tag else "#"
                if not link.startswith("http"):
                    link = f"https://www.cnn.com{link}"

                article_data = await self.__parse_article_page(client, link)
                return {"title": title, "url": link, **article_data}
            except Exception as e:
                logger.error(f"Ошибка при парсинге контейнера: {e}")
                return {}

    async def __parse_article_page(
        self, client: "ClientSession", url: str
    ) -> Dict[str, str]:
        async with semaphore:
            attempts = 0
            wait_time = 1
            while True:
                try:
                    async with client.get(
                        url, headers=self.__get_headers(), timeout=ClientTimeout(60)
                    ) as response:
                        if response.status == 429:
                            if attempts == MAX_RETRIES - 1:
                                logger.warning(
                                    f"Превышено количество попыток парсинга {url}"
                                )
                                return {"content": "", "pub_date": None}
                            logger.info(
                                f"Получен код 429. Ожидание {wait_time} секунд перед повторным запросом..."
                            )
                            await asyncio.sleep(wait_time)
                            wait_time = min(wait_time * 2, 60)
                            attempts += 1
                            continue
                        logger.info(f"{response.status}:attempt-{attempts} - {url}")
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, "lxml")

                        content_container = soup.find("div", class_="article__content")
                        paragraphs = (
                            content_container.find_all("p") if content_container else []
                        )
                        full_text = " ".join(p.text.strip() for p in paragraphs)

                        date_tag = soup.find("div", class_="timestamp vossi-timestamp")
                        raw_date = date_tag.text.strip() if date_tag else ""
                        raw_date = (
                            raw_date.replace("Updated", "")
                            .replace("Published", "")
                            .strip()
                        )

                        pub_date = None
                        if raw_date:
                            try:
                                pub_date = date_parser.parse(raw_date, ignoretz=True)
                            except ValueError as e:
                                logger.error(f"Ошибка при парсинге даты: {e}")

                        return {"content": full_text, "pub_date": pub_date}
                except ClientResponseError as e:
                    logger.error(f"Ошибка при парсинге страницы новости {url}: {e}")
                    return {"full_text": "", "pub_date": None}

    @staticmethod
    def __get_user_agent():
        user_agent = UserAgent().random
        return user_agent

    def __get_headers(self):
        return {
            "Accept": parser_settings.ACCEPT,
            "User-Agent": self.__get_user_agent(),
            "Accept-Language": parser_settings.ACCEPT_LANGUAGE,
            "Connection": parser_settings.CONNECTION,
        }
