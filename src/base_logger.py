"""Модуль для настройки логгирования."""
import logging

logger = logging.getLogger(__name__)


def set_up_logger() -> None:
    """Настроить логгер для вывода логов в консоль.

    Устанавливает формат логов и уровень логирования на INFO.
    """
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(level=logging.INFO)
    formatter = logging.Formatter(
        "[%(process)d] [%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)


set_up_logger()
