import asyncio
from asyncio import Semaphore
from typing import Any, Dict, List, Optional, Union

from aiohttp import ClientResponseError, ClientSession, ClientTimeout
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from fake_useragent import UserAgent

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
    ) -> List[Dict[str, str]]:
        """
        Парсит HTML-страницу и извлекает данные о статьях.

        Args:
            client (ClientSession): Асинхронная HTTP-сессия.
            html_content (bytes): Байтовый HTML-контент страницы.

        Returns:
            List[Dict[str, str]]: Список словарей с данными о статьях.
        """
        try:
            containers = self.__extract_containers(html_content)
            results = await self.__parse_containers(containers, client)
            return self.__filter_valid_results(results)
        except Exception as e:
            logger.error(f"Ошибка при парсинге страницы: {e}")
            return []

    @staticmethod
    def __extract_containers(html_content: bytes) -> List[Any]:
        """
        Извлекает контейнеры статей из HTML-контента.

        Args:
            html_content (bytes): Байтовый HTML-контент страницы.

        Returns:
            List[Any]: Список контейнеров статей.
        """
        soup = BeautifulSoup(html_content, "lxml")
        return soup.select("div.card.container__item")

    async def __parse_containers(
        self, containers: List[Any], client: ClientSession
    ) -> List[Dict[str, str]]:
        """
        Парсит каждый контейнер асинхронно.

        Args:
            containers (List[Any]): Список контейнеров статей.
            client (ClientSession): Асинхронная HTTP-сессия.

        Returns:
            List[Dict[str, str]]: Список словарей с результатами парсинга.
        """
        # tasks = []
        # for index, container in enumerate(containers):
        #     if container:
        #         tasks.append(self.__parse_cnn_container(container, client))
        #     if index == 10:  # Ограничение на количество парсинга для тестирования
        #         break
        tasks = (
            self.__parse_cnn_container(container, client)
            for container in containers
            if container
        )
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [
            result for result in results if isinstance(result, dict) and bool(result)
        ]

    @staticmethod
    def __filter_valid_results(
        results: List[Union[BaseException, Dict[str, str]]],
    ) -> List[Dict[str, str]]:
        """
        Фильтрует валидные результаты парсинга.

        Args:
            results (List[Union[BaseException, Dict[str, str]]]): Список результатов или исключений.

        Returns:
            List[Dict[str, str]]: Список валидных результатов.
        """
        return [result for result in results if isinstance(result, dict) and result]

    async def __parse_cnn_container(
        self, container: Any, client: ClientSession
    ) -> Dict[str, str]:
        """
        Парсит отдельный контейнер статьи.

        Args:
            container (Any): HTML-контейнер статьи.
            client (ClientSession): Асинхронная HTTP-сессия.

        Returns:
            Dict[str, str]: Словарь с данными о статье.
        """
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
            logger.error(f"Ошибка при парсинге контейнера:\n{e}")
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
            Dict[str, Optional[str]]: Словарь с текстом статьи и датой публикации.
        """
        wait_time = 1
        while True:
            try:
                async with client.get(
                    url, headers=self.__headers, timeout=ClientTimeout(60)
                ) as response:
                    if response.status == 429:
                        logger.info(
                            f"Получен код 429. Ожидание {wait_time} секунд перед повторным запросом..."
                        )
                        await asyncio.sleep(wait_time)
                        wait_time = min(wait_time * 2, 60)
                        continue
                    logger.info(f"{response.status} - {url}")
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
                        raw_date.replace("Updated", "").replace("Published", "").strip()
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
                return {"content": "", "pub_date": None}

    @property
    def __user_agent(self) -> str:
        """
        Генерирует случайный User-Agent.

        Returns:
            str: Строка с User-Agent.
        """
        return UserAgent().random

    @property
    def __headers(self) -> Dict[str, Union[str, Any]]:
        """
        Возвращает заголовки для HTTP-запросов.

        Returns:
            Dict[str, Union[str, Any]]: Словарь с заголовками.
        """
        return {
            "Accept": parser_settings.ACCEPT,
            "User-Agent": self.__user_agent,
            "Accept-Language": parser_settings.ACCEPT_LANGUAGE,
            "Connection": parser_settings.CONNECTION,
        }
