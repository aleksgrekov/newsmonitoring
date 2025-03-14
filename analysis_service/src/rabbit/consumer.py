import asyncio

from src.logger.logger_config import configure_logging
from src.rabbit.interfaces import IConnection, IMessageProcessor

logger = configure_logging(__name__)


class WorkerService:
    """
    Сервис для управления обработкой сообщений в очереди RabbitMQ.
    """

    def __init__(
        self, connection: IConnection, processor: IMessageProcessor, queue_key: str
    ):
        self._connection = connection
        self._processor = processor
        self._queue_key = queue_key

    async def run(self) -> None:
        """
        Запускает воркер: подключается к RabbitMQ и подписывается на очередь.
        """

        try:
            logger.info("Запуск воркер-сервиса")

            await self._connection.connect()

            channel = self._connection.get_channel()
            if not channel:
                raise Exception("Не удалось получить канал RabbitMQ")

            queue = await channel.declare_queue(self._queue_key, durable=True)

            # Подписка на очередь
            await queue.consume(self._processor.process_message)

            await asyncio.Future()

        except Exception as e:
            logger.error(f"Ошибка в воркер-сервисе: {e}")
        finally:
            logger.info("Остановка воркер-сервиса")
            await self._connection.disconnect()
