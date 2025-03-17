from translate_service.src.configs.base_config import Settings


class RabbitConfig(Settings):
    """Конфигурация для подключения к RabbitMQ."""

    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_LOCAL_HOST_NAME: str
    RABBITMQ_LOCAL_PORT: int

    TRANSLATE_QUEUE: str
    FANOUT_EXCHANGE: str

    @property
    def url(self) -> str:
        """
        Формирует строку подключения к RabbitMQ.
        """
        return (
            f"amqp://{self.RABBITMQ_DEFAULT_USER}:"
            f"{self.RABBITMQ_DEFAULT_PASS}@"
            f"{self.RABBITMQ_LOCAL_HOST_NAME}:"
            f"{self.RABBITMQ_LOCAL_PORT}/"
        )


rabbit_config = RabbitConfig()
