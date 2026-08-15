from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# services/commerce_service/.env
SERVICE_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=SERVICE_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Database ---
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/artisan"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # --- Stripe ---
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"


settings = Settings()
