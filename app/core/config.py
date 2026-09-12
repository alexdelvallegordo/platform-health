from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Platform Health"
    app_version: str = "0.1.0"

    awx_url: str = "http://127.0.0.1:8080"
    awx_timeout: float = 2.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
