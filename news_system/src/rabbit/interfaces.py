from abc import ABC, abstractmethod

from aio_pika.abc import AbstractChannel


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


class IMessageSender(ABC):
    @abstractmethod
    async def send_messages(self, queue_key: str) -> None:
        pass
