"""Supabase Storage upload helper and media-file CRUD.

Handles raw multipart file uploads to a Supabase storage bucket and
persists the resulting URL + metadata in the ``media_files`` table.
"""

from __future__ import annotations

import mimetypes
import uuid
from pathlib import PurePosixPath

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import Client, create_client

from ..core.config import settings
from ..models.media_files import MediaFile
from ..schemas.media_schemas import MediaFileCreate


# ---------------------------------------------------------------------------
# Supabase client (lazy singleton)
# ---------------------------------------------------------------------------

_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """Return a lazily-initialised Supabase client using the service role key."""
    global _supabase_client  # noqa: PLW0603
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
    return _supabase_client


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


async def validate_upload(file: UploadFile) -> bytes:
    """Validate file type and size, then return the file bytes.

    Raises :class:`fastapi.HTTPException` on invalid files.
    """
    # 1. Content-type check
    content_type = file.content_type
    if content_type not in settings.ALLOWED_UPLOAD_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"File type '{content_type}' is not allowed. "
                f"Accepted types: {settings.ALLOWED_UPLOAD_TYPES}"
            ),
        )

    # 2. Size check — read then compare
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )
    if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"File size {len(file_bytes)} bytes exceeds the "
                f"{settings.MAX_UPLOAD_SIZE_MB} MB limit."
            ),
        )

    return file_bytes


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------


async def upload_file(
    artwork_id: uuid.UUID,
    filename: str,
    file_bytes: bytes,
    content_type: str | None = None,
    bucket: str | None = None,
) -> dict[str, str | int]:
    """Upload *file_bytes* to Supabase Storage and return URL + metadata.

    Returns a dict with keys ``file_url``, ``file_type``, ``file_size_bytes``.
    """
    bucket = bucket or settings.SUPABASE_STORAGE_BUCKET
    content_type = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"

    ext = PurePosixPath(filename).suffix or ".bin"
    storage_path = f"{artwork_id}/{uuid.uuid4().hex}{ext}"

    client = get_supabase_client()
    client.storage.from_(bucket).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": content_type, "upsert": "true"},
    )

    # Build the public URL (Supabase storage public URLs follow this pattern).
    public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket}/{storage_path}"

    return {
        "file_url": public_url,
        "file_type": content_type,
        "file_size_bytes": len(file_bytes),
    }


# ---------------------------------------------------------------------------
# Media-file CRUD
# ---------------------------------------------------------------------------


async def create_media_file(
    db: AsyncSession,
    payload: MediaFileCreate,
) -> MediaFile:
    """Persist a media-file record."""
    media = MediaFile(**payload.model_dump())
    db.add(media)
    await db.flush()
    await db.refresh(media)
    return media


async def list_media_files(
    db: AsyncSession,
    artwork_id: uuid.UUID,
) -> tuple[list[MediaFile], int]:
    """Return all media files for an artwork, ordered by ``display_order``."""
    # Count
    count_q = await db.execute(
        select(func.count(MediaFile.id)).where(MediaFile.artwork_id == artwork_id)
    )
    total: int = count_q.scalar_one()  # type: ignore[assignment]

    # Rows
    result = await db.execute(
        select(MediaFile)
        .where(MediaFile.artwork_id == artwork_id)
        .order_by(MediaFile.display_order, MediaFile.created_at)
    )
    files = list(result.scalars().all())
    return files, total


async def delete_media_file(
    db: AsyncSession,
    media: MediaFile,
) -> None:
    """Hard-delete a media-file record."""
    await db.delete(media)
    await db.flush()


async def get_media_file_by_id(
    db: AsyncSession,
    media_id: uuid.UUID,
) -> MediaFile | None:
    """Return a single media file by its PK."""
    result = await db.execute(select(MediaFile).where(MediaFile.id == media_id))
    return result.scalar_one_or_none()
