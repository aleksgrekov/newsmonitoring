import asyncio
from asyncio import Semaphore
from typing import Any, Dict, List, Optional, Coroutine, Union, Tuple

from aiohttp import ClientResponseError, ClientSession, ClientTimeout
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from fake_useragent import UserAgent

from news_system.src.configs.parser_config import parser_settings
from news_system.src.logger.logger_config import configure_logging
from news_system.src.parser.interfaces import IArticleParser

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

        :param client: Асинхронная HTTP-сессия.
        :param html_content: Байтовый HTML-контент страницы.
        :return: Список словарей с данными о статьях.
        """
        try:
            containers = self.__extract_containers(html_content)
            tasks = self.__create_tasks_for_containers(containers, client)
            results = await self.__execute_tasks(tasks)
            return self.__filter_valid_results(results)
        except Exception as e:
            logger.error(f"Ошибка при парсинге страницы: {e}")
            return []

    @staticmethod
    def __extract_containers(html_content: bytes) -> List[Any]:
        """
        Извлекает контейнеры статей из HTML-контента.

        :param html_content: Байтовый HTML-контент страницы.
        :return: Список контейнеров статей.
        """
        soup = BeautifulSoup(html_content, "lxml")
        return soup.select("div.card.container__item")

    def __create_tasks_for_containers(
        self, containers: List[Any], client: ClientSession
    ) -> List[Coroutine[Any, Any, Dict[str, str]]]:
        """
        Создает задачи для парсинга каждого контейнера.

        :param containers: Список контейнеров статей.
        :param client: Асинхронная HTTP-сессия.
        :return: Список задач для выполнения.
        """
        return [
            self.__parse_cnn_container(async_semaphore, container, client)
            for container in containers
            if container
        ]

    @staticmethod
    async def __execute_tasks(
        tasks: List[Coroutine[Any, Any, Dict[str, str]]],
    ) -> Tuple[BaseException | Any]:
        """
        Выполняет задачи парсинга контейнеров.

        :param tasks: Список задач для выполнения.
        :return: Список результатов или исключений.
        """
        return await asyncio.gather(*tasks, return_exceptions=True)

    @staticmethod
    def __filter_valid_results(
        results: Tuple[BaseException | Any],
    ) -> List[Dict[str, str]]:
        """
        Фильтрует валидные результаты парсинга.

        :param results: Список результатов или исключений.
        :return: Список валидных результатов.
        """
        return [
            result for result in results if isinstance(result, dict) and bool(result)
        ]

    async def __parse_cnn_container(
        self,
        semaphore: Semaphore,
        container: Any,
        client: ClientSession,
    ) -> Dict[str, str]:
        """
        Парсит отдельный контейнер статьи.

        :param semaphore: Семафор для ограничения количества одновременных запросов.
        :param container: HTML-контейнер статьи.
        :param client: Асинхронная HTTP-сессия.
        :return: Словарь с данными о статье.
        """
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
                logger.error(f"Ошибка при парсинге контейнера:\n{link=}\n{e}")
                return {}

    async def __parse_article_page(
        self, client: ClientSession, url: str
    ) -> Dict[str, Optional[str]]:
        """
        Парсит страницу статьи для извлечения полного текста и даты публикации.

        :param client: Асинхронная HTTP-сессия.
        :param url: URL статьи.
        :return: Словарь с текстом статьи и датой публикации.
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

        :return: Строка с User-Agent.
        """
        return UserAgent().random

    @property
    def __headers(self) -> Dict[str, Union[str, Any]]:
        """
        Возвращает заголовки для HTTP-запросов.

        :return: Словарь с заголовками.
        """
        return {
            "Accept": parser_settings.ACCEPT,
            "User-Agent": self.__user_agent,
            "Accept-Language": parser_settings.ACCEPT_LANGUAGE,
            "Connection": parser_settings.CONNECTION,
        }
