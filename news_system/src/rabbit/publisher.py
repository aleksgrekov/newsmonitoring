from aio_pika import Message, ExchangeType
from aio_pika.abc import AbstractChannel

from news_system.src.configs.rabbit_config import rabbit_config
from news_system.src.logger.logger_config import configure_logging
from news_system.src.rabbit.interfaces import IConnection, IMessageSender
from news_system.src.rabbit.rabbit_connection import connection

logger = configure_logging(__name__)


class Publisher(IMessageSender):
    def __init__(self, conn: IConnection):
        self._connection = conn
        self._channel = None

    async def _ensure_channel(self) -> AbstractChannel:
        """
        Проверяет, есть ли активный канал, и создает новый, если его нет.

        :return: Активный канал RabbitMQ.
        :raises ConnectionError: Если канал не удалось создать.
        """
        if not self._channel or self._channel.is_closed:
            self._channel = self._connection.get_channel()

        return self._channel

    async def send_messages(
        self,
        message: str,
        exchange_name: str = rabbit_config.FANOUT_EXCHANGE,
    ) -> None:
        """
        Отправляет сообщение в Fanout Exchange.

        :param message: Сообщение для отправки.
        :param exchange_name: Имя Fanout Exchange.
        """
        try:
            channel = await self._ensure_channel()
            if not channel:
                logger.error(
                    "Невозможно отправить сообщение. Канал отсутствует или закрыт."
                )
                return

            exchange = await channel.declare_exchange(
                exchange_name, ExchangeType.FANOUT, durable=True
            )

            await exchange.publish(Message(body=message.encode()), routing_key="")
            logger.info(f"Отправлено сообщение в Exchange: {exchange_name}")

        except Exception as e:
            logger.exception("Ошибка при отправке сообщения в RabbitMQ: %s", e)


publisher: IMessageSender = Publisher(connection)
