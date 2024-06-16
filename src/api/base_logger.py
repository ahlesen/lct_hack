"""Модуль для настройки логгирования."""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def set_up_logger() -> None:
    """Настроить логгер для вывода логов в консоль и файл.

    Устанавливает формат логов и уровень логирования на INFO.
    """
    console_handler = logging.StreamHandler()

    # Генерация имени файла логов с текущей датой и временем
    log_filename = f"app_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    file_handler = logging.FileHandler(log_filename, mode='a')

    formatter = logging.Formatter(
        "[%(process)d] [%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(level=logging.INFO)


set_up_logger()
