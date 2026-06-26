from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # langsmith configuration
    langsmith_tracing: bool = True
    langsmith_endpoint: str
    langsmith_api_key: str
    langsmith_project: str

    google_api_key: str

    # read from .env file
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
