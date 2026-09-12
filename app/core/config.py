from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Platform Health"
    app_version: str = "1.0.0"
    environment: str = "development"

    awx_url: str = "http://127.0.0.1:8080"
    awx_timeout: float = 2.0

    kubernetes_timeout: float = 2.0
    kubernetes_namespace: str = "awx"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
