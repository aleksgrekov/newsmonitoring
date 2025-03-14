from aio_pika import connect_robust
from aio_pika.abc import AbstractChannel, AbstractRobustConnection

from src.configs.rabbit_config import rabbit_config
from src.logger.logger_config import configure_logging
from src.rabbit.interfaces import IConnection

logger = configure_logging(__name__)


class RabbitConnection(IConnection):
    """
    Класс для работы с RabbitMQ: подключение, отключение и отправка сообщений.
    """

    def __init__(self):
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractChannel | None = None

    async def connect(self) -> None:
        """
        Подключение к RabbitMQ и создание канала.
        """
        if self._connection and not self._connection.is_closed:
            logger.info("RabbitMQ уже подключен.")
            return

        try:
            self._connection = await connect_robust(rabbit_config.url)
            self._channel = await self._connection.channel(publisher_confirms=False)
            logger.info("Подключение к RabbitMQ. - Успех.")
        except Exception as e:
            logger.exception("При подключении к RabbitMQ произошла ошибка: %s", e)
            await self.disconnect()

    async def disconnect(self) -> None:
        """
        Отключение от RabbitMQ и закрытие канала и соединения.
        """
        try:
            if self._channel and not self._channel.is_closed:
                await self._channel.close()
            if self._connection and not self._connection.is_closed:
                await self._connection.close()
        except Exception as e:
            logger.exception("Ошибка при отключении от RabbitMQ: %s", e)
        finally:
            self._connection = None
            self._channel = None
            logger.info("Отключение от RabbitMQ завершено.")

    def get_channel(self) -> AbstractChannel:
        """
        Получение канала RabbitMQ.
        Если канал не существует, выбрасывается исключение.
        """
        if not self._channel or self._channel.is_closed:
            raise ConnectionError("Канал RabbitMQ не установлен или закрыт.")
        return self._channel


connection: IConnection = RabbitConnection()
