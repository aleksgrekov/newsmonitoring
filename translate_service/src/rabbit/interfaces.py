from abc import ABC, abstractmethod

from aio_pika.abc import AbstractChannel, AbstractIncomingMessage


class IConnection(ABC):
    """
    Интерфейс для управления соединением с брокером сообщений.
    """

    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    def get_channel(self) -> AbstractChannel | None:
        pass


class IMessageProcessor(ABC):
    """
    Интерфейс для обработки сообщений из очереди.
    """

    @abstractmethod
    async def process_message(self, message: AbstractIncomingMessage) -> None:
        pass
