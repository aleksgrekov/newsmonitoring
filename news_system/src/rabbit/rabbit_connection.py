from aio_pika import connect_robust
from aio_pika.abc import AbstractChannel, AbstractRobustConnection
from src.logger.logger_config import configure_logging
from src.configs.rabbit_config import rabbit_config
from src.rabbit.interfaces import IConnection

logger = configure_logging(__name__)


class RabbitConnection(IConnection):
    """
    Класс для работы с RabbitMQ: подключение, отключение и отправка сообщений.
    """

    _connection: AbstractRobustConnection | None = None
    _channel: AbstractChannel | None = None

    async def disconnect(self) -> None:
        """
        Отключение от RabbitMQ и закрытие канала и соединения.
        """
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

        self._connection = None
        self._channel = None
        logger.info("Отключение от RabbitMQ.")

    async def connect(self) -> None:
        """
        Подключение к RabbitMQ и создание канала.
        """
        try:
            self._connection = await connect_robust(rabbit_config.url)
            self._channel = await self._connection.channel(publisher_confirms=False)
            logger.info("Подключение к RabbitMQ.")
        except Exception as e:
            logger.exception("При подключении к RabbitMQ произошла ошибка: %s", e)
            await self.disconnect()

    def get_channel(self) -> AbstractChannel | None:
        return self._channel


connection = RabbitConnection()
