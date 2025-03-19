from aio_pika import connect_robust
from aio_pika.abc import AbstractChannel, AbstractConnection

from analysis_service.src.logger.logger_config import configure_logging
from analysis_service.src.rabbit.interfaces import IConnection

logger = configure_logging(__name__)


class RabbitConnection(IConnection):
    """
    Реализация для подключения к RabbitMQ и получения канала.

    Attributes:
        _url (str): URL для подключения к RabbitMQ.
        _connection (AbstractConnection | None): Соединение с RabbitMQ.
        _channel (AbstractChannel | None): Канал RabbitMQ.
    """

    def __init__(self, url: str):
        self._url = url
        self._connection: AbstractConnection | None = None
        self._channel: AbstractChannel | None = None

    async def connect(self) -> None:
        """
        Устанавливает соединение с RabbitMQ и создает канал.
        """
        try:
            self._connection = await connect_robust(self._url)
            self._channel = await self._connection.channel(publisher_confirms=False)
            logger.info("Подключение к RabbitMQ. - Успех.")
        except Exception as e:
            logger.exception("При подключении к RabbitMQ произошла ошибка: %s", e)
            await self.disconnect()

    async def disconnect(self) -> None:
        """
        Закрывает соединение с RabbitMQ и канал.
        """
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

        self._connection = None
        self._channel = None
        logger.info("Отключение от RabbitMQ.")

    def get_channel(self) -> AbstractChannel | None:
        """
        Возвращает канал RabbitMQ.

        Returns:
            AbstractChannel | None: Канал или None, если соединение не установлено.
        """
        return self._channel
