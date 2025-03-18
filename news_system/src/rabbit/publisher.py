from aio_pika import ExchangeType, Message
from aio_pika.abc import AbstractChannel
from news_system.src.configs.rabbit_config import rabbit_config
from news_system.src.logger.logger_config import configure_logging
from news_system.src.rabbit.interfaces import IConnection, IMessageSender
from news_system.src.rabbit.rabbit_connection import connection

logger = configure_logging(__name__)


class Publisher(IMessageSender):
    """
    Класс для отправки сообщений в RabbitMQ.

    Attributes:
        _connection (IConnection): Подключение к RabbitMQ.
        _channel (AbstractChannel | None): Канал для работы с RabbitMQ.
    """

    def __init__(self, conn: IConnection):
        self._connection = conn
        self._channel = None

    async def _ensure_channel(self) -> AbstractChannel:
        """
        Проверяет, есть ли активный канал, и создает новый, если его нет.

        Returns:
            AbstractChannel: Активный канал RabbitMQ.

        Raises:
            ConnectionError: Если канал не удалось создать.
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
        Отправляет сообщение в указанный обменник (exchange).

        Args:
            message (str): Сообщение для отправки.
            exchange_name (str): Имя обменника (exchange). По умолчанию используется FANOUT_EXCHANGE.

        Raises:
            Exception: Если произошла ошибка при отправке сообщения.
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
