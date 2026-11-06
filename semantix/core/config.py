from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "Semantix"
    database_url: str = "postgresql+asyncpg://semantix:semantix@localhost:5432/semantix"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:5173"


def get_settings() -> Settings:
    return Settings()
