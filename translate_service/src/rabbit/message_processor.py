import json

from aio_pika import Message
from aio_pika.abc import AbstractChannel, AbstractIncomingMessage
from src.logger.logger_config import configure_logging
from src.rabbit.interfaces import IMessageProcessor
from src.repositories.translator_repository import TranslatorRepository

logger = configure_logging(__name__)


class MessageProcessor(IMessageProcessor):
    """
    Процессор для обработки сообщений из очереди RabbitMQ.

    Attributes:
        _channel (AbstractChannel): Канал RabbitMQ.
    """

    def __init__(
        self,
        header: str,
        max_retry: int,
        critical_count: int,
        channel: AbstractChannel,
    ) -> None:
        self._header = header
        self._max_retry = max_retry
        self._critical_count = critical_count
        self._channel = channel

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        """
        Обрабатывает входящее сообщение.

        Args:
            message (AbstractIncomingMessage): Входящее сообщение из очереди.
        """

        retries = self._get_retry_count(message)

        try:
            self._parse_message_body(message)
            await TranslatorRepository.translate()
            await message.ack()
            logger.info("Перевод новостей окончен! - Translate Service")
        except ValueError as exc:
            logger.error(
                "Ошибка при обработке сообщения: %s",
                exc,
                exc_info=True,
            )

            retries -= 1
            if retries > self._critical_count:
                await self._requeue_message(message, retries)
            else:
                logger.error(
                    "Превышен лимит попыток обработки. Сообщение отклонено.",
                )
                await message.reject(requeue=False)

    def _get_retry_count(self, message: AbstractIncomingMessage) -> int:
        """
        Получает количество оставшихся попыток обработки сообщения.

        Args:
            message (AbstractIncomingMessage): Входящее сообщение.

        Returns:
            int: Количество оставшихся попыток.
        """
        return int(message.headers.get(self._header, self._max_retry))

    @staticmethod
    def _parse_message_body(message: AbstractIncomingMessage) -> None:
        """
        Парсит тело сообщения.

        Args:
            message (AbstractIncomingMessage): Входящее сообщение.

        Returns:
            dict: Распарсенное тело сообщения.

        Raises:
            ValueError: Если тело сообщения не может быть распарсено.
        """
        try:
            body = message.body.decode()
            data = json.loads(body)
            message = data.get("message", "нет ключа 'message'")

            logger.info(
                "Получено сообщение: %s",
                message,
            )
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.exception("Ошибка при парсинге тела сообщения:")
            raise ValueError("Неверный формат сообщения") from exc

    async def _requeue_message(
        self, message: AbstractIncomingMessage, retries: int
    ) -> None:
        """
        Отправляет сообщение обратно в очередь для повторной обработки.

        Args:
            message (AbstractIncomingMessage): Входящее сообщение.
            retries (int): Количество оставшихся попыток.
        """
        try:
            msg = message.routing_key
            if not msg:
                logger.warning(f"{msg=}")
                return

            await self._channel.default_exchange.publish(
                Message(
                    body=message.body,
                    headers={self._header: retries},
                ),
                routing_key=msg,
            )
            logger.warning(
                "Повторная отправка сообщения. Осталось попыток: %d",
                retries,
            )

        except Exception as exc:
            logger.exception(
                "Ошибка при повторной отправке сообщения в очередь: %s",
                exc,
            )
