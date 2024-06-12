import logging

logger = logging.getLogger(__name__)


def set_up_logger() -> None:
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(level=logging.INFO)
    formatter = logging.Formatter(
        "[%(process)d] [%(asctime)s] [%(levelname)s] %(message)s", datefmt="%s"
    )
    handler.setFormatter(formatter)


set_up_logger()
