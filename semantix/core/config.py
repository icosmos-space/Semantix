from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "Semantix"
    database_url: str = "postgresql+asyncpg://semantix:semantix@localhost:5432/semantix"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:5173"
    # Comma-separated hosts allowed for Functional HTTP calls (SSRF guard)
    http_allowlist_hosts: str = "localhost,127.0.0.1"
    http_timeout_s: float = 15.0
    http_max_response_bytes: int = 1_000_000


def get_settings() -> Settings:
    return Settings()

