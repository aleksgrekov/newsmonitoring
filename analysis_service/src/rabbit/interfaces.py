from abc import ABC, abstractmethod
from aio_pika.abc import AbstractChannel, AbstractConnection


class IConnection(ABC):
    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    def get_channel(self) -> AbstractChannel | None:
        pass
