import json

from aio_pika.abc import AbstractChannel, AbstractIncomingMessage

from translate_service.src.logger.logger_config import configure_logging
from translate_service.src.rabbit.interfaces import IMessageProcessor
from translate_service.src.repositories.translator_repository import (
    TranslatorRepository,
)

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

            await TranslatorRepository.translate()
            await message.ack()
            logger.info(f"Анализ новостей окончен! - Translate Service")

        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
            await message.nack()  # Отправляем сообщение обратно в очередь
