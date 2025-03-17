from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from aiohttp import ClientSession

from news_system.src.schemas.news_schemas import NewsResponseSchema


class IHttpRequester(ABC):
    """
    Интерфейс для выполнения HTTP-запросов.
    """

    @abstractmethod
    async def fetch_and_compare(
        self, client: ClientSession, last_modified: Optional[str]
    ) -> Optional[str]:
        """
        Проверяет, изменился ли контент, сравнивая заголовок Last-Modified.

        :param client: Асинхронная HTTP-сессия.
        :param last_modified: Последнее значение заголовка Last-Modified.
        :return: Новое значение заголовка Last-Modified или None, если контент не изменился.
        """
        pass

    @abstractmethod
    async def send_request(
        self, client: ClientSession, modified_header: Optional[str]
    ) -> Optional[bytes]:
        """
        Отправляет GET-запрос для получения HTML-контента.

        :param client: Асинхронная HTTP-сессия.
        :param modified_header: Заголовок Last-Modified.
        :return: Байтовый HTML-контент или None в случае ошибки.
        """
        pass


class IArticleParser(ABC):
    """
    Интерфейс для парсинга статей.
    """

    @abstractmethod
    async def parse_page(
        self, client: ClientSession, html_content: bytes
    ) -> List[Dict[str, str]]:
        """
        Парсит HTML-страницу и извлекает данные о статьях.

        :param client: Асинхронная HTTP-сессия.
        :param html_content: Байтовый HTML-контент страницы.
        :return: Список словарей с данными о статьях.
        """
        pass


class INewsParser(ABC):
    """
    Интерфейс для сбора новостей.
    """

    @abstractmethod
    async def collect_news(self) -> NewsResponseSchema:
        """
        Собирает новости.

        :return: Объект NewsResponseSchema с данными о новостях.
        """
        pass
