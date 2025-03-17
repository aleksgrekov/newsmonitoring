import asyncio

from translate_service.src.configs.rabbit_config import rabbit_config
from translate_service.src.logger.logger_config import configure_logging
from translate_service.src.rabbit.consumer import WorkerService
from translate_service.src.rabbit.message_processor import MessageProcessor
from translate_service.src.rabbit.rabbit_connection import RabbitConnection

logger = configure_logging(__name__)

if __name__ == "__main__":
    """
    Запускает основной процесс воркер-сервиса. В случае остановки сервиса вручную
    или из-за ошибки выводится соответствующий лог.
    """
    try:
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
