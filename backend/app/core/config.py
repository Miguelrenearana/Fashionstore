from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "FashionStore API"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:4200,http://localhost:3000"

    database_url: str = "postgresql+psycopg://fashion:change-me@localhost:5432/fashionstore"

    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    payment_gateway: str = "mock"
    base_url_app: str = "http://localhost:8000"
    pagosnet_api_key: str = ""
    pagosnet_encryption_key: str = ""
    pagosnet_base_url: str = "https://sandbox.pagosnet.bo/api"

    static_qr_merchant_id: str = "FS001"
    static_qr_merchant_name: str = "FashionStore"
    static_qr_merchant_city: str = "La Paz"
    static_qr_account: str = "12345678901234567890"
    static_qr_webhook_secret: str = ""
    static_qr_timeout_minutes: int = 10
    static_qr_auto_complete_seconds: int = 30

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    mail_from: str = "noreply@fashionstore.dev"

    recommendation_embedding_model: str = "all-MiniLM-L6-v2"
    recommendation_batch_size: int = 64

    # Ollama (IA local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_sql_model: str = "codellama"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
