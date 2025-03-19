import json

from aio_pika.abc import AbstractChannel, AbstractIncomingMessage

from analysis_service.src.logger.logger_config import configure_logging
from analysis_service.src.rabbit.interfaces import IMessageProcessor
from analysis_service.src.repositories.news_repository import NewsRepository

logger = configure_logging(__name__)


class MessageProcessor(IMessageProcessor):
    """
    Процессор для обработки сообщений из очереди RabbitMQ.

    Attributes:
        _channel (AbstractChannel): Канал RabbitMQ.
    """

    def __init__(self, channel: AbstractChannel):
        self._channel = channel

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        """
        Обрабатывает входящее сообщение.

        Args:
            message (AbstractIncomingMessage): Входящее сообщение из очереди.
        """
        try:
            body = message.body.decode()
            data = json.loads(body)
            logger.info(
                f"Получено сообщение: {data['message']} из очереди {message.routing_key}"
            )

            await NewsRepository.analyze_and_save_news()
            await message.ack()
            logger.info("Анализ новостей завершен! - Analysis Service")

        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
            await message.nack()  # Отправляем сообщение обратно в очередь
