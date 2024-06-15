"""Запуск и настройка FastAPI приложения.

Этот модуль включает функции для создания и запуска сервера FastAPI
с использованием uvicorn и uvloop.
"""

import asyncio

import uvicorn
import uvloop
from fastapi import FastAPI

from src.api.base_logger import logger
from src.api.service import router
from src.api.settings import Settings

settings = Settings()


def create_app() -> FastAPI:
    """Создать и настроить экземпляр FastAPI приложения.

    :return: Настроенное FastAPI приложение.
    :rtype: FastAPI
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="REST API Search Yappy Service",
        version="dev",
        debug=settings.DEBUG,
        contact={"name": "Andrey Vlasov", "email": "ahlesen@gmail.com"},
        license_info={
            "name": "Apache 2.0",
            "url": "http://www.apache.org/licenses/LICENSE-2.0.html",
        },
        terms_of_service="http://swagger.io/terms/",
    )
    app.include_router(router)

    return app


async def run_server(app: FastAPI) -> None:
    """Настроить и запустить сервер uvicorn.

    :param app: FastAPI приложение для запуска.
    :type app: FastAPI
    :raises Exception: Пропуск исключений во время выполнения сервера.
    """
    config = uvicorn.Config(
        app, host=settings.APP_HOST, port=settings.APP_PORT, reload=settings.DEBUG
    )
    server = uvicorn.Server(config=config)
    logger.info("Server is running on %s:%s", settings.APP_HOST, settings.APP_PORT)

    try:
        await server.serve()
    except Exception as exc:
        logger.exception(f"An error occurred while running the server: {exc}")


async def main() -> None:
    """Основная точка входа для настройки и запуска приложения."""
    uvloop.install()  # Install uvloop to make asyncio faster
    app = create_app()
    await run_server(app)


if __name__ == "__main__":
    asyncio.run(main(), debug=settings.DEBUG)
