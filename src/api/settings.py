"""Модуль для управления настройками приложения.

Этот модуль содержит класс Settings, который загружает конфигурацию
из окружения или файла .env.
"""

from pydantic import BaseSettings, PositiveInt


class Settings(BaseSettings):
    """Класс для управления настройками приложения.

    Настройки загружаются из файла .env или переменных окружения.

    Атрибуты:
        APP_NAME (str): Имя приложения.
        APP_HOST (str): Хост для запуска приложения.
        APP_PORT (PositiveInt): Порт для запуска приложения.
        DEBUG (bool): Режим отладки.
    """

    model_config = {
        "env_file": ".env",
    }

    # Base
    APP_NAME: str = "yappy_search"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: PositiveInt = 8080

    # Model paths

    # Dev tools
    DEBUG: bool = True
