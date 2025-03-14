from aio_pika import Message

from news_system.src.configs.rabbit_config import rabbit_config
from news_system.src.logger.logger_config import configure_logging
from news_system.src.rabbit.interfaces import IConnection, IMessageSender
from news_system.src.rabbit.rabbit_connection import connection

logger = configure_logging(__name__)


class Publisher(IMessageSender):

    def __init__(self, conn: IConnection):
        self._connection = conn
        self._channel = None

    async def _ensure_channel(self):
        """
        Проверяет, есть ли активный канал, и создает новый, если его нет.
        """
        if not self._channel or self._channel.is_closed:
            self._channel = self._connection.get_channel()

        return self._channel

    async def send_messages(
        self, message: str, queue_key: str = rabbit_config.PARSER_QUEUE
    ) -> None:
        """
        Отправляет сообщение в RabbitMQ. Если канал закрыт, пытается восстановить соединение.
        """
        channel = await self._ensure_channel()
        if not channel:
            logger.error(
                "Невозможно отправить сообщение. Канал отсутствует или закрыт."
            )
            return

        try:
            await channel.default_exchange.publish(
                Message(body=message.encode()), routing_key=queue_key
            )
            logger.info(f"Отправлено сообщение в очередь: {queue_key}")
        except Exception as e:
            logger.exception("Ошибка при отправке сообщения в RabbitMQ: %s", e)


publisher: IMessageSender = Publisher(connection)
