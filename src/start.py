import asyncio

import uvicorn
import uvloop
from fastapi import FastAPI

from src.service import router
from src.settings import Settings
from src.base_logger import logger

settings = Settings()

def create_app() -> FastAPI:
    """
    Create and configure an instance of the FastAPI application.

    Returns:
        FastAPI: The configured FastAPI application.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="REST API Search Yappy Service",
        version="dev",
        debug=settings.DEBUG,
    )
    app.include_router(router)

    return app

async def run_server(app: FastAPI) -> None:
    """
    Configure and run the uvicorn server.

    Args:
        app (FastAPI): The FastAPI application to serve.

    Raises:
        Exception: Propagates exceptions from the server runtime.
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
    """
    Main entry point for the application setup and execution.
    """
    uvloop.install()  # Install uvloop to make asyncio faster
    app = create_app()
    await run_server(app)

if __name__ == "__main__":
    asyncio.run(main(), debug=settings.DEBUG)