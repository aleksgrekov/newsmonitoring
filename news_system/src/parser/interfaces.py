from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from aiohttp import ClientSession

from news_system.src.schemas.news_schemas import NewsResponseSchema


class IHttpRequester(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def fetch_and_compare(self, client: "ClientSession") -> Optional[str]:
        pass

    @abstractmethod
    async def send_request(
        self, client: "ClientSession", modified_header: Optional[str]
    ) -> Optional[bytes]:
        pass


class IArticleParser(ABC):

    @abstractmethod
    async def parse_page(
        self, client: "ClientSession", html_content: bytes
    ) -> List[Dict[str, str]]:
        pass


class INewsParser(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def collect_news(self) -> NewsResponseSchema:
        pass
