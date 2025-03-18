from abc import ABC, abstractmethod
from aio_pika.abc import AbstractChannel


class IConnection(ABC):
    """
    Интерфейс для управления подключением к RabbitMQ.

    Методы:
        - connect: Устанавливает соединение с RabbitMQ.
        - disconnect: Закрывает соединение с RabbitMQ.
        - get_channel: Возвращает канал для работы с RabbitMQ.
    """

    @abstractmethod
    async def connect(self) -> None:
        """
        Устанавливает соединение с RabbitMQ.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Закрывает соединение с RabbitMQ.
        """
        pass

    @abstractmethod
    def get_channel(self) -> AbstractChannel:
        """
        Возвращает канал для работы с RabbitMQ.

        Returns:
            AbstractChannel: Канал RabbitMQ.

        Raises:
            ConnectionError: Если канал не установлен или закрыт.
        """
        pass


class IMessageSender(ABC):
    """
    Интерфейс для отправки сообщений в RabbitMQ.

    Методы:
        - send_messages: Отправляет сообщение в указанный обменник (exchange).
    """

    @abstractmethod
    async def send_messages(self, message: str, exchange_name: str) -> None:
        """
        Отправляет сообщение в указанный обменник (exchange).

        Args:
            message (str): Сообщение для отправки.
            exchange_name (str): Имя обменника (exchange).
        """
        pass
