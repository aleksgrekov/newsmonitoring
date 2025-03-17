from typing import Any, Dict, Optional, Union

from aiohttp import ClientSession, ClientTimeout
from fake_useragent import UserAgent

from news_system.src.configs.parser_config import parser_settings
from news_system.src.logger.logger_config import configure_logging
from news_system.src.parser.interfaces import IHttpRequester

logger = configure_logging(__name__)


class HttpRequester(IHttpRequester):
    def __init__(self):
        self.__url: str = parser_settings.NEWS_URL

    async def send_request(
        self, client: "ClientSession", modified_header: Optional[str]
    ) -> Optional[bytes]:
        if not modified_header:
            logger.error("Не передан модификатор заголовка или контент не изменился!")
            return None

        try:
            async with client.get(
                self.__url, headers=self.__headers, timeout=ClientTimeout(15)
            ) as response:
                if response.status == 200:
                    content = await response.read()
                    return content
                else:
                    logger.error(f"Ошибка при запросе: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Ошибка при отправке запроса: {e}")
            return None

    async def fetch_and_compare(
        self, client: "ClientSession", last_modified: Optional[str]
    ) -> Optional[str]:
        async with client.head(self.__url, timeout=ClientTimeout(15)) as response:
            if response.status != 200:
                logger.error(f"Не удалось получить заголовки для {self.__url}")
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
        user_agent = UserAgent().random
        return user_agent

    @property
    def __headers(self) -> Dict[str, Union[str, Any]]:
        return {
            "Accept": parser_settings.ACCEPT,
            "User-Agent": self.__user_agent,
            "Accept-Language": parser_settings.ACCEPT_LANGUAGE,
            "Connection": parser_settings.CONNECTION,
        }
