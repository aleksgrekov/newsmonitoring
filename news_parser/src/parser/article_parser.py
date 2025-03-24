import asyncio
from asyncio import Semaphore
from typing import Dict, List, Optional

from aiohttp import ClientResponseError, ClientSession, ClientTimeout
from bs4 import BeautifulSoup, Tag
from dateutil import parser as date_parser
from fake_useragent import FakeUserAgentError, UserAgent
from src.configs.parser_config import parser_settings
from src.logger.logger_config import configure_logging
from src.parser.interfaces import IArticleParser

logger = configure_logging(__name__)
async_semaphore = Semaphore(50)


class ArticleParser(IArticleParser):
    """
    Парсер для извлечения данных о статьях из HTML-контента.
    """

    async def parse_page(
        self, client: ClientSession, html_content: bytes
    ) -> List[Dict[str, Optional[str]]]:
        """
        Парсит HTML-страницу и извлекает данные о статьях.

        Args:
            client (ClientSession): Асинхронная HTTP-сессия.
            html_content (bytes): Байтовый HTML-контент страницы.

        Returns:
            List[Dict[str, Optional[str]]]: Список словарей
            с данными о статьях.
        """

        containers = self.__extract_containers(html_content)
        results = await self.__parse_containers(containers, client)
        return self.__filter_valid_results(results)

    @staticmethod
    def __extract_containers(html_content: bytes) -> List[Tag]:
        """
        Извлекает контейнеры статей из HTML-контента.

        Args:
            html_content (bytes): Байтовый HTML-контент страницы.

        Returns:
            List[Tag]: Список контейнеров статей.
        """
        try:
            soup = BeautifulSoup(html_content, "lxml")
            return soup.select("div.card.container__item")
        except (AttributeError, TypeError) as exc:
            logger.error("Ошибка при извлечении контейнеров: %s", exc)
            return []

    async def __parse_containers(
        self, containers: List[Tag], client: ClientSession
    ) -> List[Dict[str, Optional[str]]]:
        """
        Парсит каждый контейнер асинхронно.

        Args:
            containers (List[Tag]): Список контейнеров статей.
            client (ClientSession): Асинхронная HTTP-сессия.

        Returns:
            List[Dict[str, Optional[str]]]: Список словарей
            с результатами парсинга.
        """
        try:
            tasks = (
                self.__parse_cnn_container(container, client)
                for container in containers
                if container
            )
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return [
                res
                for res in results
                if isinstance(
                    res,
                    dict,
                )
                and bool(res)
            ]
        except (
            asyncio.TimeoutError,
            ClientResponseError,
            AttributeError,
        ) as exc:
            logger.error("Ошибка при парсинге контейнеров: %s", exc)
            return []

    @staticmethod
    def __filter_valid_results(
        results: List[Dict[str, Optional[str]]],
    ) -> List[Dict[str, Optional[str]]]:
        """
        Фильтрует валидные результаты парсинга.

        Args:
            results (List[Dict[str, Optional[str]]]): Список результатов.

        Returns:
            List[Dict[str, Optional[str]]]: Список валидных результатов.
        """
        return [res for res in results if isinstance(res, dict) and res]

    async def __parse_cnn_container(
        self, container: Tag, client: ClientSession
    ) -> Dict[str, Optional[str]]:
        """
        Парсит отдельный контейнер статьи.

        Args:
            container (Tag): HTML-контейнер статьи.
            client (ClientSession): Асинхронная HTTP-сессия.

        Returns:
            Dict[str, Optional[str]]: Словарь с данными о статье.
        """
        try:
            headline_tag = container.find(
                "span",
                class_="container__headline-text",
            )
            title = headline_tag.text.strip() if headline_tag else "No title"

            link_tag = container.find("a", href=True)
            link = (
                str(
                    link_tag.get(
                        "href",
                        "#",
                    )
                )
                if isinstance(link_tag, Tag)
                else "#"
            )
            link = (
                f"https://www.cnn.com{link}"
                if link and not link.startswith("http")
                else link
            )

            article_data = await self.__parse_article_page(client, link or "#")
            return {"title": title or "", "url": link or "", **article_data}
        except (AttributeError, TypeError) as exc:
            logger.error("Ошибка при парсинге контейнера: %s", exc)
            return {}

    async def __parse_article_page(
        self, client: ClientSession, url: str
    ) -> Dict[str, Optional[str]]:
        """
        Парсит страницу статьи для извлечения полного текста и даты публикации.

        Args:
            client (ClientSession): Асинхронная HTTP-сессия.
            url (str): URL статьи.

        Returns:
            Dict[str, Optional[str]]: Словарь
            с текстом статьи и датой публикации.
        """
        wait_time = 1
        while True:
            try:
                async with client.get(
                    url, headers=self.__headers, timeout=ClientTimeout(60)
                ) as response:
                    if response.status == 429:
                        logger.info(
                            "Получен код 429. "
                            "Ожидание %s секунд перед повторным запросом...",
                            wait_time,
                        )
                        await asyncio.sleep(wait_time)
                        wait_time = min(wait_time * 2, 60)
                        continue
                    logger.info("%s - %s", response.status, url)
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, "lxml")

                    content_container = soup.find(
                        "div",
                        class_="article__content",
                    )
                    paragraphs = (
                        content_container.find_all("p")
                        if content_container
                        and isinstance(
                            content_container,
                            Tag,
                        )
                        else []
                    )
                    full_text = " ".join(p.text.strip() for p in paragraphs)

                    date_tag = soup.find(
                        "div",
                        class_="timestamp vossi-timestamp",
                    )
                    raw_date = date_tag.text.strip() if date_tag else ""

                    updated_date = raw_date.replace("Updated", "")
                    published_date = updated_date.replace("Published", "")
                    raw_date = published_date.strip()

                    try:
                        pub_date = (
                            date_parser.parse(
                                raw_date,
                                ignoretz=True,
                            ).isoformat()
                            if raw_date
                            else None
                        )
                    except ValueError as exc:
                        logger.error("Ошибка при парсинге даты: %s", exc)
                        pub_date = None

                    return {"content": full_text, "pub_date": pub_date}
            except (
                ClientResponseError,
                asyncio.TimeoutError,
                AttributeError,
                ValueError,
            ) as exc:
                logger.error(
                    "Ошибка при парсинге страницы новости %s: %s",
                    url,
                    exc,
                )
                return {"content": "", "pub_date": None}

    @property
    def __user_agent(self) -> str:
        """
        Генерирует случайный User-Agent.

        Returns:
            str: Строка с User-Agent.
        """
        try:
            return UserAgent().random
        except FakeUserAgentError as exc:
            logger.error("Ошибка при генерации User-Agent: %s", exc)
            return "Mozilla/5.0"

    @property
    def __headers(self) -> Dict[str, str]:
        """
        Возвращает заголовки для HTTP-запросов.

        Returns:
            Dict[str, str]: Словарь с заголовками.
        """
        return {
            "Accept": parser_settings.ACCEPT,
            "User-Agent": self.__user_agent,
            "Accept-Language": parser_settings.ACCEPT_LANGUAGE,
            "Connection": parser_settings.CONNECTION,
        }
