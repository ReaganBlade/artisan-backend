"""Dummy Personalization Service endpoints for the feed and interactions.

The real implementation reads the pre-calculated ``personalized_feed_cache``
and appends to the ``user_interactions`` ledger. These stubs return the same
contract.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from ..dummy_data import (
    FEED_CACHE,
    INTERACTIONS,
    INTERACTION_TYPES,
    USER_ID,
    feed_result,
    new_id,
)

router = APIRouter(tags=["feed", "interactions"])


@router.get("/feed")
async def get_feed(
    user_id: str | None = Query(None, description="Defaults to the mock user."),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """Personalized artwork feed for a user (homepage / 'for you' rail)."""
    uid = user_id or USER_ID
    cache = FEED_CACHE
    cached_ids = cache["cached_artwork_ids"]
    items = [feed_result(i) for i in cached_ids]
    return {
        "user_id": uid,
        "last_calculated_at": cache["last_calculated_at"],
        "items": items[offset : offset + limit],
        "total": len(items),
        "limit": limit,
        "offset": offset,
    }


@router.post("/interactions", status_code=status.HTTP_201_CREATED)
async def record_interaction(payload: dict[str, Any]) -> dict[str, Any]:
    """Record a user↔artwork interaction (like, view, follow_artist, save, share).

    ``payload``: ``{"user_id": "...", "artwork_id": "...", "interaction_type": "like"}``
    """
    interaction_type = payload.get("interaction_type")
    if interaction_type not in INTERACTION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"interaction_type must be one of {INTERACTION_TYPES}.",
        )
    if not payload.get("artwork_id"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="artwork_id is required.",
        )
    return {
        "id": new_id(),
        "user_id": payload.get("user_id", USER_ID),
        "artwork_id": payload["artwork_id"],
        "interaction_type": interaction_type,
        "created_at": "2026-08-16T09:00:00Z",
    }


@router.get("/interactions/me")
async def my_interactions(
    user_id: str | None = Query(None, description="Defaults to the mock user."),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """A user's interaction history (liked/saved artworks, activity feed)."""
    uid = user_id or USER_ID
    items = [i for i in INTERACTIONS if i["user_id"] == uid]
    return {
        "user_id": uid,
        "items": items[offset : offset + limit],
        "total": len(items),
        "limit": limit,
        "offset": offset,
    }
