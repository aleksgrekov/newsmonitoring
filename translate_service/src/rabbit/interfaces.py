from abc import ABC, abstractmethod

from aio_pika.abc import AbstractChannel, AbstractIncomingMessage


class IConnection(ABC):
    """
    Интерфейс для управления соединением с брокером сообщений.

    Методы:
        - connect: Устанавливает соединение с брокером.
        - disconnect: Закрывает соединение с брокером.
        - get_channel: Возвращает канал для работы с брокером.
    """

    @abstractmethod
    async def connect(self) -> None:
        """
        Устанавливает соединение с брокером сообщений.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Закрывает соединение с брокером сообщений.
        """
        pass

    @abstractmethod
    def get_channel(self) -> AbstractChannel | None:
        """
        Возвращает канал для работы с брокером сообщений.

        Returns:
            AbstractChannel | None: Канал или None, если соединение не установлено.
        """
        pass


class IMessageProcessor(ABC):
    """
    Интерфейс для обработки сообщений из очереди.

    Методы:
        - process_message: Обрабатывает входящее сообщение.
    """

    @abstractmethod
    async def process_message(self, message: AbstractIncomingMessage) -> None:
        """
        Обрабатывает входящее сообщение.

        Args:
            message (AbstractIncomingMessage): Входящее сообщение из очереди.
        """
        pass
