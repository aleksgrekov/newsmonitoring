import json
from pathlib import Path
from typing import Optional

from aiohttp import ClientSession, ClientTimeout
from fake_useragent import UserAgent

from src.configs.parser_config import parser_settings
from src.logger.logger_config import configure_logging
from src.parser.interfaces import IHttpRequester

logger = configure_logging(__name__)


class HttpRequester(IHttpRequester):
    def __init__(self):
        self.__url = parser_settings.NEWS_URL
        self.__last_modified_file = Path("last_modified.json")
        self.last_modified = None
        self.__load_last_modified()

    async def fetch_and_compare(self, client: "ClientSession") -> Optional[str]:
        async with client.head(self.__url, timeout=ClientTimeout(15)) as response:
            if response.status != 200:
                logger.error(f"Не удалось получить заголовки для {self.__url}")
                return None

            last_modified_header = response.headers.get("x-last-modified")
            if not last_modified_header:
                logger.warning("Заголовок 'x-last-modified' отсутствует.")
                return None
            logger.info(f"Last-Modified: {last_modified_header}")

            if last_modified_header == self.last_modified:
                logger.info("Контент не изменился. Используем сохраненный файл.")
                return None

            return last_modified_header

    async def send_request(
        self, client: "ClientSession", modified_header: Optional[str]
    ) -> Optional[bytes]:
        if not modified_header:
            logger.error("Не передан модификатор заголовка или контент не изменился!")
            return None

        try:
            async with client.get(
                self.__url, headers=self.__get_headers(), timeout=ClientTimeout(15)
            ) as response:
                if response.status == 200:
                    content = await response.read()
                    self.__save_last_modified(modified_header)
                    return content
                else:
                    logger.error(f"Ошибка при запросе: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Ошибка при отправке запроса: {e}")
            return None

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

    def __load_last_modified(self):
        if self.__last_modified_file.exists():
            try:
                with self.__last_modified_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.last_modified = data.get("last_modified")
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Ошибка при загрузке last_modified: {e}")
                self.last_modified = None

    def __save_last_modified(self, value: str):
        try:
            with self.__last_modified_file.open("w", encoding="utf-8") as f:
                json.dump({"last_modified": value}, f)
        except OSError as e:
            logger.error(f"Ошибка при сохранении last_modified: {e}")
