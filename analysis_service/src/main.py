import asyncio
from analysis_service.src.configs.rabbit_config import rabbit_config
from analysis_service.src.logger.logger_config import configure_logging
from analysis_service.src.rabbit.consumer import WorkerService
from analysis_service.src.rabbit.message_processor import MessageProcessor
from analysis_service.src.rabbit.rabbit_connection import RabbitConnection

logger = configure_logging(__name__)


def run_service() -> None:
    """
    Запускает сервис обработки сообщений из RabbitMQ.

    Raises:
        Exception: Логирует ошибку в случае сбоя.
    """
    try:
        logger.info("Запуск сервиса обработки сообщений...")

        connection = RabbitConnection(rabbit_config.url)
        processor = MessageProcessor(connection.get_channel())
        worker = WorkerService(
            connection,
            processor,
            rabbit_config.FANOUT_EXCHANGE,
            rabbit_config.ANALYSIS_QUEUE,
        )

        asyncio.run(worker.run())

    except KeyboardInterrupt:
        logger.info("Сервис был остановлен вручную.")

    except Exception as e:
        logger.exception("Критическая ошибка в работе сервиса: %s", e)


if __name__ == "__main__":
    run_service()
