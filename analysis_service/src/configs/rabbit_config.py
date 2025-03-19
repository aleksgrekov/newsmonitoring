from analysis_service.src.configs.base_config import Settings


class RabbitConfig(Settings):
    """
    Класс для управления настройками подключения к RabbitMQ.

    Настройки загружаются из переменных окружения или файла `.env`.

    Attributes:
        RABBITMQ_DEFAULT_USER (str): Имя пользователя RabbitMQ.
        RABBITMQ_DEFAULT_PASS (str): Пароль пользователя RabbitMQ.
        RABBITMQ_LOCAL_HOST_NAME (str): Хост RabbitMQ.
        RABBITMQ_LOCAL_PORT (int): Порт RabbitMQ.

        ANALYSIS_QUEUE (str): Название очереди сообщений.
        FANOUT_EXCHANGE (str): Название fanout exchange.
    """

    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_LOCAL_HOST_NAME: str
    RABBITMQ_LOCAL_PORT: int

    ANALYSIS_QUEUE: str
    FANOUT_EXCHANGE: str

    @property
    def url(self) -> str:
        """
        Формирует строку подключения к RabbitMQ.

        Returns:
            str: Строка подключения к RabbitMQ.
        """
        return "amqp://{user}:{password}@{host}:{port}/".format(
            user=self.RABBITMQ_DEFAULT_USER,
            password=self.RABBITMQ_DEFAULT_PASS,
            host=self.RABBITMQ_LOCAL_HOST_NAME,
            port=self.RABBITMQ_LOCAL_PORT,
        )


rabbit_config = RabbitConfig()
