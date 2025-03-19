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
            logger.info("Соединение с RabbitMQ установлено")

            channel = self._connection.get_channel()
            if not channel:
                logger.error("Не удалось получить канал RabbitMQ")
                raise Exception("Не удалось получить канал RabbitMQ")
            logger.info("Канал RabbitMQ успешно получен")

            exchange = await channel.declare_exchange(
                self._exchange_name, ExchangeType.FANOUT, durable=True
            )
            logger.info(f"Обменник {self._exchange_name} успешно объявлен")

            queue = await channel.declare_queue(
                self._queue_name, durable=True, exclusive=True
            )
            logger.info(f"Очередь {self._queue_name} успешно объявлена")

            await queue.bind(exchange, routing_key="")
            logger.info(
                f"Очередь {self._queue_name} привязана к обменнику {self._exchange_name}"
            )

            await queue.consume(self._processor.process_message)
            logger.info(f"Начато потребление сообщений из очереди {self._queue_name}")

            await asyncio.Future()

        except Exception as e:
            logger.error(f"Ошибка в воркер-сервисе: {e}", exc_info=True)
        finally:
            logger.info("Остановка воркер-сервиса")
            await self._connection.disconnect()
            logger.info("Отключение от RabbitMQ")
