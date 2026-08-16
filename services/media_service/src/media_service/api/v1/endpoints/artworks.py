"""Dummy Media Service endpoints for the Artwork catalog.

All handlers return deterministic mock data (see ``dummy_data.py``) that mirrors
the shapes of the SQLAlchemy models in ``media_service.models``. Replace the
``dummy_`` helpers with real repository calls as the backend is built out.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from ..dummy_data import (
    ARTWORKS,
    MEDIA_FILES,
    _MEDIA_URL_BASE,
    new_id,
    paginate,
)

router = APIRouter(prefix="/artworks", tags=["artworks"])


def _find_artwork(artwork_id: str) -> dict[str, Any]:
    for artwork in ARTWORKS:
        if artwork["id"] == artwork_id:
            return artwork
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artwork not found.")


@router.get("")
async def list_artworks(
    status_filter: str | None = Query(None, alias="status", description="Filter by artwork status."),
    art_type: str | None = Query(None, description="Filter by art type (Painting, Print, ...)."),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """List published artworks, optionally filtered and paginated.

    Used by the frontend wall / browse / search-result grids.
    """
    items = [
        a
        for a in ARTWORKS
        if (status_filter is None or a["status"] == status_filter)
        and (art_type is None or a["art_type"] == art_type)
    ]
    return paginate(items, limit, offset)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_artwork(payload: dict[str, Any]) -> dict[str, Any]:
    """Create an artwork draft (dummy — no persistence).

    ``payload`` accepts any subset of artwork fields; ``id`` is always generated.
    """
    artwork_id = new_id()
    return {
        "id": artwork_id,
        "profile_id": payload.get("profile_id", "11111111-1111-1111-1111-111111111101"),
        "title": payload.get("title", "Untitled"),
        "description": payload.get("description"),
        "art_type": payload.get("art_type", "Print"),
        "price": payload.get("price"),
        "status": payload.get("status", "draft"),
        "primary_media_url": payload.get("primary_media_url"),
        "created_at": "2026-08-16T09:00:00Z",
        "updated_at": "2026-08-16T09:00:00Z",
    }


@router.get("/{artwork_id}")
async def get_artwork(artwork_id: str) -> dict[str, Any]:
    """Full artwork record for the detail page / lightbox."""
    return _find_artwork(artwork_id)


@router.patch("/{artwork_id}")
async def update_artwork(artwork_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Update artwork fields (dummy — returns the payload merged onto the mock)."""
    artwork = _find_artwork(artwork_id)
    artwork.update(payload)
    artwork["updated_at"] = "2026-08-16T09:00:00Z"
    return artwork


@router.delete("/{artwork_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artwork(artwork_id: str) -> None:
    """Remove an artwork (dummy — mock list is untouched)."""
    _find_artwork(artwork_id)
    return None


@router.get("/{artwork_id}/media")
async def list_artwork_media(artwork_id: str) -> list[dict[str, Any]]:
    """All media files attached to an artwork (gallery / detail carousel)."""
    _find_artwork(artwork_id)
    return [m for m in MEDIA_FILES if m["artwork_id"] == artwork_id]


@router.post("/{artwork_id}/media", status_code=status.HTTP_201_CREATED)
async def attach_media(artwork_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Attach a media file to an artwork (dummy — no upload, no persistence)."""
    _find_artwork(artwork_id)
    return {
        "id": new_id(),
        "artwork_id": artwork_id,
        "file_url": payload.get(
            "file_url", f"{_MEDIA_URL_BASE}/{artwork_id}/uploaded.jpg"
        ),
        "file_type": payload.get("file_type", "image/jpeg"),
        "file_size_bytes": payload.get("file_size_bytes"),
        "display_order": payload.get("display_order", 0),
        "created_at": "2026-08-16T09:00:00Z",
    }
