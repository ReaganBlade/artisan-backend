"""Artwork catalog endpoints backed by real persistence."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...dependencies import get_db
from ....schemas.artwork_schemas import (
    ArtworkCreate,
    ArtworkListResponse,
    ArtworkResponse,
    ArtworkUpdate,
)
from ....services import artwork_service

router = APIRouter(prefix="/artworks", tags=["artworks"])


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


@router.get("", response_model=ArtworkListResponse)
async def list_artworks(
    profile_id: uuid.UUID | None = Query(None, description="Filter by profile."),
    status_filter: str | None = Query(None, alias="status", description="Filter by status."),
    art_type: str | None = Query(None, description="Filter by art type."),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> ArtworkListResponse:
    """List artworks with optional filters and pagination."""
    artworks, total = await artwork_service.list_artworks(
        db,
        profile_id=profile_id,
        status_filter=status_filter,
        art_type=art_type,
        limit=limit,
        offset=offset,
    )
    return ArtworkListResponse(
        items=[ArtworkResponse.model_validate(a) for a in artworks],
        total=total,
        limit=limit,
        offset=offset,
    )


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=ArtworkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_artwork(
    payload: ArtworkCreate,
    db: AsyncSession = Depends(get_db),
) -> ArtworkResponse:
    """Create a new artwork."""
    artwork = await artwork_service.create_artwork(db, payload)
    return ArtworkResponse.model_validate(artwork)


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------


@router.get("/{artwork_id}", response_model=ArtworkResponse)
async def get_artwork(
    artwork_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ArtworkResponse:
    """Full artwork record for the detail page."""
    artwork = await artwork_service.get_artwork_by_id(db, artwork_id)
    if artwork is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artwork not found.",
        )
    return ArtworkResponse.model_validate(artwork)


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


@router.patch("/{artwork_id}", response_model=ArtworkResponse)
async def update_artwork(
    artwork_id: uuid.UUID,
    payload: ArtworkUpdate,
    db: AsyncSession = Depends(get_db),
) -> ArtworkResponse:
    """Partial update of artwork fields."""
    artwork = await artwork_service.get_artwork_by_id(db, artwork_id)
    if artwork is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artwork not found.",
        )
    updated = await artwork_service.update_artwork(db, artwork, payload)
    return ArtworkResponse.model_validate(updated)


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


@router.delete(
    "/{artwork_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_artwork(
    artwork_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an artwork (cascades to media_files)."""
    artwork = await artwork_service.get_artwork_by_id(db, artwork_id)
    if artwork is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artwork not found.",
        )
    await artwork_service.delete_artwork(db, artwork)



