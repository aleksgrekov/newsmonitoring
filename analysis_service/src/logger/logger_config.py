import logging


def configure_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Настраивает и возвращает логгер с указанным именем и уровнем логирования.

    Args:
        name (str): Имя логгера.
        level (int, optional): Уровень логирования. По умолчанию `logging.INFO`.

    Returns:
        logging.Logger: Настроенный логгер.
    """
    log_format = "[%(asctime)s.%(msecs)03d] %(funcName)20s %(module)s:%(lineno)d %(levelname)-8s - %(message)s"

    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format=log_format,
    )

    return logging.getLogger(name)
