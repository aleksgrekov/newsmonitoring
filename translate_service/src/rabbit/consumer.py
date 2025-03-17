import asyncio

from aio_pika import ExchangeType

from translate_service.src.logger.logger_config import configure_logging
from translate_service.src.rabbit.interfaces import IConnection, IMessageProcessor

logger = configure_logging(__name__)


class WorkerService:
    """
    Сервис для управления обработкой сообщений в очереди RabbitMQ.
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

            channel = self._connection.get_channel()
            if not channel:
                raise Exception("Не удалось получить канал RabbitMQ")

            exchange = await channel.declare_exchange(
                self._exchange_name, ExchangeType.FANOUT, durable=True
            )

            queue = await channel.declare_queue(self._queue_name, durable=True)

            await queue.bind(exchange, routing_key="")

            await queue.consume(self._processor.process_message)

            await asyncio.Future()

        except Exception as e:
            logger.error(f"Ошибка в воркер-сервисе: {e}")
        finally:
            logger.info("Остановка воркер-сервиса")
            await self._connection.disconnect()
