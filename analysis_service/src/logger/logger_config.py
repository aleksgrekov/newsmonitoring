import logging


def configure_logging(
    name: str,
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Настройка логирования.

    :param name: Имя логгера.
    :param level: Уровень логирования (по умолчанию INFO).
    :return: Настроенный логгер.
    """

    # Формат логирования
    log_format = "[%(asctime)s.%(msecs)03d] %(funcName)20s %(module)s:%(lineno)d %(levelname)-8s - %(message)s"

    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format=log_format,
    )

    return logging.getLogger(name)
