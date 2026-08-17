from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# services/auth_service/.env
SERVICE_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env.

    The .env file lives at the service root (services/auth_service/.env),
    resolved relative to this module so the app works from any CWD.
    """

    model_config = SettingsConfigDict(
        env_file=SERVICE_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Database ---
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/artisan"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    AUTO_MIGRATE: bool = True

    # --- Auth / JWT ---
    # Dev-only default (>= 32 bytes for HS256). Override in .env / production.
    JWT_SECRET_KEY: str = "dev-only-insecure-secret-change-me-0123456789"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # --- Supabase ---
    # Anon/publishable key. The client is created lazily, so the service runs
    # fine without these until the Supabase client is actually used.
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""


settings = Settings()
