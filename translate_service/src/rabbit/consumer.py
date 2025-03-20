import asyncio

from aio_pika import ExchangeType
from aio_pika.abc import AbstractChannel, AbstractExchange, AbstractQueue
from src.logger.logger_config import configure_logging
from src.rabbit.interfaces import IConnection, IMessageProcessor

logger = configure_logging(__name__)


class WorkerService:
    """
    Сервис для управления обработкой сообщений в очереди RabbitMQ.

    Attributes:
        _connection (IConnection): Подключение к RabbitMQ.
        _processor (IMessageProcessor): Процессор для обработки сообщений.
        _exchange_name (str): Имя обменника.
        _queue_name (str): Имя очереди.
    """

    def __init__(
        self,
        connection: IConnection,
        processor: IMessageProcessor,
        exchange_name: str,
        queue_name: str,
    ):
        self._connection = connection
        self._processor = processor
        self._exchange_name = exchange_name
        self._queue_name = queue_name

    async def run(self) -> None:
        """
        Запускает воркер: подключается к RabbitMQ и подписывается на очередь.
        """
        try:
            logger.info("Запуск Translate Service")

            await self._connection.connect()
            logger.info("Соединение с RabbitMQ установлено")

            channel = self._connection.get_channel()
            if not channel:
                logger.error("Не удалось получить канал RabbitMQ")
                raise Exception("Не удалось получить канал RabbitMQ")
            logger.info("Канал RabbitMQ успешно получен")

            exchange = await self._declare_exchange(channel)
            queue = await self._declare_queue(channel)
            await self._bind_queue_to_exchange(queue, exchange)

            await queue.consume(self._processor.process_message)
            logger.info(
                "Начато потребление сообщений из очереди %s",
                self._queue_name,
            )

            await asyncio.Future()

        except Exception as exc:
            logger.error("Ошибка в воркер-сервисе: %s", exc, exc_info=True)
        finally:
            logger.info("Остановка воркер-сервиса")
            await self._connection.disconnect()
            logger.info("Отключение от RabbitMQ")

    async def _declare_exchange(
        self,
        channel: AbstractChannel,
    ) -> AbstractExchange:
        """
        Объявляет обменник в RabbitMQ.

        Args:
            channel: Канал RabbitMQ.

        Returns:
            Объявленный обменник.
        """
        exchange = await channel.declare_exchange(
            self._exchange_name, ExchangeType.FANOUT, durable=True
        )
        logger.info("Обменник %s успешно объявлен", self._exchange_name)
        return exchange

    async def _declare_queue(self, channel: AbstractChannel) -> AbstractQueue:
        """
        Объявляет очередь в RabbitMQ.

        Args:
            channel: Канал RabbitMQ.

        Returns:
            Объявленная очередь.
        """
        queue = await channel.declare_queue(self._queue_name, durable=True)
        logger.info("Очередь %s успешно объявлена", self._queue_name)
        return queue

    async def _bind_queue_to_exchange(self, queue, exchange) -> None:
        """
        Привязывает очередь к обменнику.

        Args:
            queue: Очередь RabbitMQ.
            exchange: Обменник RabbitMQ.
        """
        await queue.bind(exchange, routing_key="")
        logger.info(
            "Очередь %s привязана к обменнику %s",
            self._queue_name,
            self._exchange_name,
        )
