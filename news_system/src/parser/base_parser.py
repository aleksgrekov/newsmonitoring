from abc import ABC, abstractmethod
from typing import List, Dict


class BaseParser(ABC):
    @abstractmethod
    async def collect_news(self) -> List[Dict[str, str]]:
        pass
