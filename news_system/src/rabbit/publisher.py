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
        _exchange (ExchangeType | None): Обменник RabbitMQ для отправки сообщений.
    """

    def __init__(
        self, conn: IConnection, exchange_name: str = rabbit_config.FANOUT_EXCHANGE
    ):
        """
        Инициализация Publisher с созданием канала и обменника.

        Args:
            conn (IConnection): Подключение к RabbitMQ.
            exchange_name (str): Имя обменника для отправки сообщений.
        """
        self._connection = conn
        self._channel = None
        self._exchange = None
        self._exchange_name = exchange_name

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

    async def _ensure_exchange(self) -> None:
        """
        Проверяет, есть ли созданный обменник, и создает его, если нет.

        Raises:
            Exception: Если не удалось создать обменник.
        """
        if not self._exchange:
            channel = await self._ensure_channel()
            self._exchange = await channel.declare_exchange(
                self._exchange_name, ExchangeType.FANOUT, durable=True
            )
            logger.info(f"Обменник {self._exchange_name} был создан.")

    async def send_messages(
        self,
        message: str,
    ) -> None:
        """
        Отправляет сообщение в указанный обменник (exchange).

        Args:
            message (str): Сообщение для отправки.

        Raises:
            Exception: Если произошла ошибка при отправке сообщения.
        """
        try:
            await self._ensure_exchange()
            if not self._exchange:
                logger.error("Невозможно отправить сообщение. Обменник отсутствует.")
                return

            await self._exchange.publish(Message(body=message.encode()), routing_key="")
            logger.info(f"Отправлено сообщение в Exchange: {self._exchange_name}")

        except Exception as e:
            logger.exception("Ошибка при отправке сообщения в RabbitMQ: %s", e)


publisher: IMessageSender = Publisher(connection)
