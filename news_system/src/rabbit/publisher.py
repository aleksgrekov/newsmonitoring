import json
from typing import Dict

from aio_pika import Message

from src.configs.rabbit_config import rabbit_config
from src.rabbit.interfaces import IMessageSender, IConnection
from src.rabbit.rabbit_connection import connection
from src.logger.logger_config import configure_logging

logger = configure_logging(__name__)


class Publisher(IMessageSender):

    def __init__(self, conn: IConnection):
        self._connection = conn
        self._channel = self._connection.get_channel()

    async def send_messages(
        self,
        message: Dict[str, int],
        queue_key: str = rabbit_config.PARSER_QUEUE,
    ) -> None:

        if self._channel is None or self._channel.is_closed:
            logger.error("Невозможно отправить сообщение. Канал закрыт.")
            return

        body = json.dumps(message).encode()
        try:
            await self._channel.default_exchange.publish(
                Message(body=body), routing_key=queue_key
            )
            logger.info(f"Отправка сообщения в очередь: {queue_key}")
        except Exception as e:
            logger.exception("Ошибка при отправке сообщения в RabbitMQ: %s", e)


publisher = Publisher(connection)
