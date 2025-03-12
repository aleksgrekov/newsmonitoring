import json
from pathlib import Path
from typing import Optional

import requests
from src.configs.parser_config import parser_settings
from src.logger.logger_config import configure_logging

logger = configure_logging(__name__)


class HttpRequester:
    def __init__(self):
        self.__url = parser_settings.NEWS_URL
        self.__headers = self.__create_headers
        self.__last_modified_file = Path("last_modified.json")
        self.last_modified = None
        self.__load_last_modified()

    @property
    def __create_headers(self):
        return {
            "Accept": parser_settings.YOUR_ACCEPT_HEADER,
            "User-Agent": parser_settings.YOUR_USER_AGENT_HEADER,
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

    def fetch_and_compare(self) -> Optional[str]:
        head_response = requests.head(self.__url)
        if head_response.status_code != 200:
            logger.error(f"Не удалось получить заголовки для {self.__url}")
            return None

        last_modified_header = head_response.headers.get("x-last-modified")
        logger.info(f"Last-Modified: {last_modified_header}")

        if last_modified_header == self.last_modified:
            logger.info("Контент не изменился. Используем сохраненный файл.")
            return None

        return last_modified_header

    def send_request(self, modified_header: Optional[str]) -> Optional[bytes]:
        if not modified_header:
            logger.error("Не передан модификатор заголовка или контент не изменился!")
            return None

        try:
            response = requests.get(self.__url, headers=self.__headers, timeout=10)
            if response.status_code == 200:
                self.__save_last_modified(modified_header)
                return response.content
            else:
                logger.error(f"Ошибка при запросе: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при отправке запроса: {e}")
            return None
