"""Pydantic schemas for the MediaFile entity."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


class MediaFileBase(BaseModel):
    """Fields shared by every media-file variant."""

    artwork_id: uuid.UUID
    file_url: str = Field(..., max_length=512)
    file_type: str = Field(..., max_length=50)
    file_size_bytes: int | None = None
    display_order: int = Field(default=0, ge=0)


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


class MediaFileCreate(MediaFileBase):
    """Payload accepted by ``POST /artworks/{id}/media``."""

    pass


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


class MediaFileUpdate(BaseModel):
    """Payload accepted by ``PATCH /media/{id}``.

    All fields are optional — only supplied keys are updated.
    """

    file_url: str | None = Field(default=None, max_length=512)
    file_type: str | None = Field(default=None, max_length=50)
    file_size_bytes: int | None = None
    display_order: int | None = Field(default=None, ge=0)


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------


class MediaFileResponse(MediaFileBase):
    """Wire-format returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


# ---------------------------------------------------------------------------
# List envelope
# ---------------------------------------------------------------------------


class MediaFileListResponse(BaseModel):
    """Paginated list of media files."""

    items: list[MediaFileResponse]
    total: int
