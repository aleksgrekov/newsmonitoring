from src.configs.rabbit_config import rabbit_config
from src.logger.logger_config import configure_logging
from src.rabbit.consumer import WorkerService
from src.rabbit.message_processor import MessageProcessor
from src.rabbit.rabbit_connection import RabbitConnection

logger = configure_logging(__name__)


class RabbitFactory:
    """Фабрика для создания экземпляров WorkerService и его зависимостей."""

    @staticmethod
    def create_worker():
        """
        Создает экземпляр WorkerService с настраиваемыми параметрами.

        Returns:
            WorkerService: Экземпляр WorkerService.
        """
        connection = RabbitConnection(rabbit_config.url)
        processor = MessageProcessor(
            rabbit_config.X_RETRIES_HEADER,
            rabbit_config.ATTEMPTS_COUNT,
            rabbit_config.CRITICAL_ATTEMPTS_VALUE,
            connection.get_channel(),
        )
        return WorkerService(
            connection,
            processor,
            rabbit_config.FANOUT_EXCHANGE,
            rabbit_config.ANALYSIS_QUEUE,
        )


factory: RabbitFactory = RabbitFactory()
