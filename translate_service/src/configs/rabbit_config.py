from src.configs.base_config import Settings


class RabbitConfig(Settings):
    """
    Класс для управления настройками подключения к RabbitMQ.

    Настройки загружаются из переменных окружения или файла `.env`.

    Attributes:
        RABBITMQ_DEFAULT_USER (str): Имя пользователя RabbitMQ.
        RABBITMQ_DEFAULT_PASS (str): Пароль пользователя RabbitMQ.
        RABBITMQ_LOCAL_HOST_NAME (str): Хост RabbitMQ.
        RABBITMQ_LOCAL_PORT (int): Порт RabbitMQ.

        X_RETRIES_HEADER (str): хедер для отправки количества
        попыток обработки сообщения

        ATTEMPTS_COUNT (int): количество попыток отправки сообщения
        CRITICAL_ATTEMPTS_VALUE (int): критическое значение, при котором
        сообщение будет отменено (по умолчанию равно 0).

        TRANSLATE_QUEUE (str): Название очереди сообщений.
        FANOUT_EXCHANGE (str): Название fanout exchange.
    """

    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_LOCAL_HOST_NAME: str
    RABBITMQ_LOCAL_PORT: int

    X_RETRIES_HEADER: str
    ATTEMPTS_COUNT: int
    CRITICAL_ATTEMPTS_VALUE: int

    TRANSLATE_QUEUE: str
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
