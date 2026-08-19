"""Pydantic schemas for the Profile entity."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


class ProfileBase(BaseModel):
    """Fields shared by every profile variant."""

    user_id: uuid.UUID
    username: str = Field(..., min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    bio: str | None = None
    avatar_url: str | None = None
    cover_image_url: str | None = None
    social_links: dict[str, str] | None = None


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


class ProfileCreate(ProfileBase):
    """Payload accepted by ``POST /profiles``."""

    pass


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


class ProfileUpdate(BaseModel):
    """Payload accepted by ``PATCH /profiles/{id}``.

    All fields are optional — only supplied keys are updated.
    """

    display_name: str | None = Field(default=None, min_length=1, max_length=100)
    bio: str | None = None
    avatar_url: str | None = None
    cover_image_url: str | None = None
    social_links: dict[str, str] | None = None


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------


class ProfileResponse(ProfileBase):
    """Wire-format returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
