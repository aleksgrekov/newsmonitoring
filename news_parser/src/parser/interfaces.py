from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from aiohttp import ClientSession
from src.schemas.news_schemas import NewsResponseSchema


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

        Args:
            client (ClientSession): Асинхронная HTTP-сессия.
            last_modified (Optional[str]):
            Последнее значение заголовка Last-Modified.

        Returns:
            Optional[str]: Новое значение заголовка Last-Modified,
            если контент изменился, иначе None.
        """
        pass

    @abstractmethod
    async def send_request(
        self, client: ClientSession, modified_header: Optional[str]
    ) -> Optional[bytes]:
        """
        Отправляет GET-запрос для получения HTML-контента.

        Args:
            client (ClientSession):
            Асинхронная HTTP-сессия.

            modified_header (Optional[str]):
            Заголовок Last-Modified, если он есть.

        Returns:
            Optional[bytes]: Байтовый HTML-контент или None в случае ошибки.
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

        Args:
            client (ClientSession): Асинхронная HTTP-сессия.
            html_content (bytes): Байтовый HTML-контент страницы.

        Returns:
            List[Dict[str, str]]:
            Список словарей с данными о статьях (например, заголовок, URL).
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

        Returns:
            NewsResponseSchema: Объект с данными о новостях.
        """
        pass
