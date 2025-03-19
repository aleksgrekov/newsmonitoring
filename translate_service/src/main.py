import asyncio

from src.configs.rabbit_config import rabbit_config
from src.logger.logger_config import configure_logging
from src.rabbit.consumer import WorkerService
from src.rabbit.message_processor import MessageProcessor
from src.rabbit.rabbit_connection import RabbitConnection

logger = configure_logging(__name__)


def run_service() -> None:
    """
    Запускает основной процесс воркер-сервиса.

    Этот метод инициализирует подключение к RabbitMQ, создает обработчик сообщений,
    настраивает воркер для получения задач и выполняет асинхронную работу. В случае
    ошибки или остановки вручную выводится соответствующий лог.

    """
    try:
        logger.info("Запуск сервиса перевода текстов...")

        connection = RabbitConnection(rabbit_config.url)
        processor = MessageProcessor(connection.get_channel())
        worker = WorkerService(
            connection,
            processor,
            rabbit_config.FANOUT_EXCHANGE,
            rabbit_config.TRANSLATE_QUEUE,
        )

        asyncio.run(worker.run())

    except KeyboardInterrupt:
        logger.info("Сервис был остановлен вручную!")

    except Exception as exc:
        logger.exception("Критическая ошибка в работе сервиса: %s", exc)


# Запуск основного процесса
if __name__ == "__main__":
    run_service()
