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

    AUTO_MIGRATE: bool = True

    # --- Supabase Storage ---
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET: str = "artworks"

    # --- Upload Validation ---
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_IMAGE_TYPES: list[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "image/svg+xml",
    ]
    ALLOWED_DOCUMENT_TYPES: list[str] = [
        "text/plain",
        "text/csv",
        "application/pdf",
        "application/json",
    ]
    ALLOWED_3D_TYPES: list[str] = [
        "model/gltf-binary",
        "model/gltf+json",
        "application/octet-stream",
    ]
    ALLOWED_AUDIO_TYPES: list[str] = [
        "audio/mpeg",
        "audio/wav",
        "audio/ogg",
        "audio/flac",
    ]
    ALLOWED_VIDEO_TYPES: list[str] = [
        "video/mp4",
        "video/webm",
        "video/quicktime",
    ]

    @property
    def ALLOWED_UPLOAD_TYPES(self) -> list[str]:
        """Flat list of all allowed MIME types."""
        return (
            self.ALLOWED_IMAGE_TYPES
            + self.ALLOWED_DOCUMENT_TYPES
            + self.ALLOWED_3D_TYPES
            + self.ALLOWED_AUDIO_TYPES
            + self.ALLOWED_VIDEO_TYPES
        )

    @property
    def MAX_UPLOAD_SIZE_BYTES(self) -> int:
        """Max upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


settings = Settings()
