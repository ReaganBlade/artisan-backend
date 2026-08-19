"""Endpoints for media-file management.

Handles raw multipart file uploads to Supabase Storage and the
associated ``media_files`` database records.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...dependencies import get_db
from ....schemas.media_schemas import (
    MediaFileCreate,
    MediaFileListResponse,
    MediaFileResponse,
)
from ....services import artwork_service, upload_service

router = APIRouter(prefix="/artworks/{artwork_id}/media", tags=["media"])


# ---------------------------------------------------------------------------
# List media files for an artwork
# ---------------------------------------------------------------------------


@router.get("", response_model=MediaFileListResponse)
async def list_artwork_media(
    artwork_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> MediaFileListResponse:
    """Return all media files attached to an artwork, ordered by display_order."""
    # Verify artwork exists
    artwork = await artwork_service.get_artwork_by_id(db, artwork_id)
    if artwork is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artwork not found.",
        )
    files, total = await upload_service.list_media_files(db, artwork_id)
    return MediaFileListResponse(
        items=[MediaFileResponse.model_validate(f) for f in files],
        total=total,
    )


# ---------------------------------------------------------------------------
# Upload a file
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=MediaFileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_artwork_media(
    artwork_id: uuid.UUID,
    file: UploadFile,
    display_order: int = 0,
    db: AsyncSession = Depends(get_db),
) -> MediaFileResponse:
    """Upload a raw file to Supabase Storage and attach it to the artwork.

    The file is streamed into memory then uploaded via the Supabase SDK.
    """
    # Verify artwork exists
    artwork = await artwork_service.get_artwork_by_id(db, artwork_id)
    if artwork is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artwork not found.",
        )

    # Validate file type and size (raises HTTPException on failure)
    file_bytes = await upload_service.validate_upload(file)

    # Upload to Supabase Storage
    upload_meta = await upload_service.upload_file(
        artwork_id=artwork_id,
        filename=file.filename or "upload.bin",
        file_bytes=file_bytes,
        content_type=file.content_type,
    )

    # Persist the DB record
    payload = MediaFileCreate(
        artwork_id=artwork_id,
        file_url=upload_meta["file_url"],
        file_type=upload_meta["file_type"],
        file_size_bytes=upload_meta["file_size_bytes"],
        display_order=display_order,
    )
    media = await upload_service.create_media_file(db, payload)
    return MediaFileResponse.model_validate(media)


# ---------------------------------------------------------------------------
# Delete a single media file
# ---------------------------------------------------------------------------


@router.delete(
    "/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_artwork_media(
    artwork_id: uuid.UUID,
    media_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a media file from the artwork."""
    media = await upload_service.get_media_file_by_id(db, media_id)
    if media is None or media.artwork_id != artwork_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found for this artwork.",
        )
    await upload_service.delete_media_file(db, media)
