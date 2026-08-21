"""Artist-profile endpoints backed by real persistence."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...dependencies import get_db
from ....schemas.artwork_schemas import ArtworkListResponse, ArtworkResponse
from ....schemas.profile_schemas import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
)
from ....services import artwork_service, profile_service

router = APIRouter(prefix="/profiles", tags=["profiles"])


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


@router.get("", response_model=dict)
async def list_profiles(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List artist profiles (browse-artists page)."""
    profiles, total = await profile_service.list_profiles(db, limit=limit, offset=offset)
    return {
        "items": [ProfileResponse.model_validate(p) for p in profiles],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


# ---------------------------------------------------------------------------
# Read by username (convenience route — must come before {profile_id})
# ---------------------------------------------------------------------------


@router.get("/by-username/{username}", response_model=ProfileResponse)
async def get_profile_by_username(
    username: str,
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """Resolve a profile by username (used for ``/artist/{username}`` routing)."""
    profile = await profile_service.get_profile_by_username(db, username)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )
    return ProfileResponse.model_validate(profile)


# ---------------------------------------------------------------------------
# Read by ID
# ---------------------------------------------------------------------------


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """Public artist profile (artist page header, artwork attribution)."""
    profile = await profile_service.get_profile_by_id(db, profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )
    return ProfileResponse.model_validate(profile)


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    payload: ProfileCreate,
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """Create a new artist profile."""
    profile = await profile_service.create_profile(db, payload)
    return ProfileResponse.model_validate(profile)


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: uuid.UUID,
    payload: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """Partial update of profile display fields."""
    profile = await profile_service.get_profile_by_id(db, profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )
    updated = await profile_service.update_profile(db, profile, payload)
    return ProfileResponse.model_validate(updated)


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


@router.delete(
    "/{profile_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_profile(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an artist profile."""
    profile = await profile_service.get_profile_by_id(db, profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )
    await profile_service.delete_profile(db, profile)


# ---------------------------------------------------------------------------
# Profile's artworks
# ---------------------------------------------------------------------------


@router.get("/{profile_id}/artworks", response_model=ArtworkListResponse)
async def list_profile_artworks(
    profile_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> ArtworkListResponse:
    """All artworks by one artist (artist page grid)."""
    # Verify profile exists
    profile = await profile_service.get_profile_by_id(db, profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )
    artworks, total = await artwork_service.list_artworks(
        db, profile_id=profile_id, limit=limit, offset=offset,
    )
    return ArtworkListResponse(
        items=[ArtworkResponse.model_validate(a) for a in artworks],
        total=total,
        limit=limit,
        offset=offset,
    )
