from logging import INFO, StreamHandler, basicConfig

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    DATABASE_URL: str


logger_config = {
    'level': INFO,
    'encoding': 'utf-8',
    'format': '%(asctime)s %(levelname)s: %(message)s',
    'handlers': [StreamHandler()],
}

basicConfig(**logger_config)
