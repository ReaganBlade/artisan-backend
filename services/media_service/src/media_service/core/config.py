from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# services/media_service/.env
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

    # --- Supabase Storage ---
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET: str = "artworks"


settings = Settings()
