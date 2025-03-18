from typing import Any, Dict, Optional, Union

from aiohttp import ClientSession, ClientTimeout
from fake_useragent import UserAgent

from news_system.src.configs.parser_config import parser_settings
from news_system.src.logger.logger_config import configure_logging
from news_system.src.parser.interfaces import IHttpRequester

logger = configure_logging(__name__)


class HttpRequester(IHttpRequester):
    """
    Класс для выполнения HTTP-запросов.
    """

    def __init__(self):
        """
        Инициализация HTTP-запросчика.
        """
        self.__url = parser_settings.NEWS_URL
        self.__headers = self.__generate_headers()

    def __generate_headers(self) -> Dict[str, Union[str, Any]]:
        """
        Генерирует заголовки для HTTP-запросов.

        Returns:
            Dict[str, Union[str, Any]]: Словарь с заголовками.
        """
        return {
            "Accept": parser_settings.ACCEPT,
            "User-Agent": self.__user_agent,
            "Accept-Language": parser_settings.ACCEPT_LANGUAGE,
            "Connection": parser_settings.CONNECTION,
        }

    async def send_request(
        self, client: ClientSession, modified_header: Optional[str]
    ) -> Optional[bytes]:
        """
        Отправляет GET-запрос для получения HTML-контента.

        Args:
            client (ClientSession): Асинхронная HTTP-сессия.
            modified_header (Optional[str]): Заголовок Last-Modified.

        Returns:
            Optional[bytes]: Байтовый HTML-контент или None в случае ошибки.
        """
        if not modified_header:
            logger.error("Не передан модификатор заголовка или контент не изменился!")
            return None

        try:
            return await self.__fetch_content(client)
        except Exception as e:
            logger.error(f"Ошибка при отправке запроса: {e}")
            return None

    async def __fetch_content(self, client: ClientSession) -> Optional[bytes]:
        """
        Выполняет GET-запрос и возвращает контент.

        Args:
            client (ClientSession): Асинхронная HTTP-сессия.

        Returns:
            Optional[bytes]: Байтовый HTML-контент или None в случае ошибки.
        """
        async with client.get(
            self.__url, headers=self.__headers, timeout=ClientTimeout(15)
        ) as response:
            if response.status == 200:
                return await response.read()
            else:
                logger.error(
                    f"Ошибка при запросе к {self.__url}: Статус {response.status}"
                )
                return None

    async def fetch_and_compare(
        self, client: ClientSession, last_modified: Optional[str]
    ) -> Optional[str]:
        """
        Проверяет, изменился ли контент, сравнивая заголовок Last-Modified.

        Args:
            client (ClientSession): Асинхронная HTTP-сессия.
            last_modified (Optional[str]): Последнее значение заголовка Last-Modified.

        Returns:
            Optional[str]: Новое значение заголовка Last-Modified или None, если контент не изменился.
        """
        async with client.head(self.__url, timeout=ClientTimeout(15)) as response:
            if response.status != 200:
                logger.error(
                    f"Не удалось получить заголовки для {self.__url}. Статус: {response.status}"
                )
                return None

            last_modified_header = response.headers.get("x-last-modified")
            if not last_modified_header:
                logger.warning("Заголовок 'x-last-modified' отсутствует.")
                return None

            logger.info(f"Last-Modified: {last_modified_header}")

            if last_modified_header == last_modified:
                logger.info("Контент не изменился. В БД актуальные данные.")
                return None
            return last_modified_header

    @property
    def __user_agent(self) -> str:
        """
        Генерирует случайный User-Agent.

        Returns:
            str: Строка с User-Agent.
        """
        return UserAgent().random
