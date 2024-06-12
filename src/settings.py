from pydantic import BaseSettings, PositiveInt


class Settings(BaseSettings):
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
