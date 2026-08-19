"""Pydantic schemas for the Artwork entity."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


class ArtworkBase(BaseModel):
    """Fields shared by every artwork variant."""

    profile_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    art_type: str = Field(..., min_length=1, max_length=50)
    price: Decimal | None = Field(default=None, ge=Decimal("0"))
    status: str = Field(default="DRAFT", max_length=20)
    primary_media_url: str | None = None


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


class ArtworkCreate(ArtworkBase):
    """Payload accepted by ``POST /artworks``."""

    pass


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


class ArtworkUpdate(BaseModel):
    """Payload accepted by ``PATCH /artworks/{id}``.

    All fields are optional — only supplied keys are updated.
    """

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    art_type: str | None = Field(default=None, min_length=1, max_length=50)
    price: Decimal | None = Field(default=None, ge=Decimal("0"))
    status: str | None = Field(default=None, max_length=20)
    primary_media_url: str | None = None


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------


class ArtworkResponse(ArtworkBase):
    """Wire-format returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# List envelope
# ---------------------------------------------------------------------------


class ArtworkListResponse(BaseModel):
    """Paginated list of artworks."""

    items: list[ArtworkResponse]
    total: int
    limit: int
    offset: int
