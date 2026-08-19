"""Business-logic / repository layer for Artwork CRUD."""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.artworks import Artwork
from ..schemas.artwork_schemas import ArtworkCreate, ArtworkUpdate


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------


async def get_artwork_by_id(
    db: AsyncSession,
    artwork_id: uuid.UUID,
) -> Artwork | None:
    """Return a single artwork by its PK, or ``None``."""
    result = await db.execute(select(Artwork).where(Artwork.id == artwork_id))
    return result.scalar_one_or_none()


async def list_artworks(
    db: AsyncSession,
    *,
    profile_id: uuid.UUID | None = None,
    status_filter: str | None = None,
    art_type: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[Sequence[Artwork], int]:
    """Return a filtered, paginated list of artworks and the total count."""
    query = select(Artwork)

    if profile_id is not None:
        query = query.where(Artwork.profile_id == profile_id)
    if status_filter is not None:
        query = query.where(Artwork.status == status_filter)
    if art_type is not None:
        query = query.where(Artwork.art_type == art_type)

    # Total count (with same filters)
    count_q = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total: int = count_q.scalar_one()  # type: ignore[assignment]

    # Page
    query = query.order_by(Artwork.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    artworks = result.scalars().all()
    return artworks, total


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


async def create_artwork(
    db: AsyncSession,
    payload: ArtworkCreate,
) -> Artwork:
    """Persist a new artwork and return it."""
    artwork = Artwork(**payload.model_dump())
    db.add(artwork)
    await db.flush()
    await db.refresh(artwork)
    return artwork


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


async def update_artwork(
    db: AsyncSession,
    artwork: Artwork,
    payload: ArtworkUpdate,
) -> Artwork:
    """Apply partial updates to an existing artwork."""
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(artwork, field, value)
    await db.flush()
    await db.refresh(artwork)
    return artwork


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


async def delete_artwork(
    db: AsyncSession,
    artwork: Artwork,
) -> None:
    """Hard-delete an artwork (cascades to media_files)."""
    await db.delete(artwork)
    await db.flush()
