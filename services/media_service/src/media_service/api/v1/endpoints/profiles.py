"""Dummy Media Service endpoints for artist profiles.

Payloads mirror the ``Profile`` model in ``media_service.models``.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status

from ..dummy_data import ARTWORKS, PROFILES, new_id, paginate

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _find_profile(profile_id: str) -> dict[str, Any]:
    for profile in PROFILES:
        if profile["id"] == profile_id:
            return profile
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")


@router.get("")
async def list_profiles(limit: int = 20, offset: int = 0) -> dict[str, Any]:
    """List artist profiles (browse-artists page)."""
    return paginate(PROFILES, limit, offset)


@router.get("/by-username/{username}", include_in_schema=False)
async def get_profile_by_username(username: str) -> dict[str, Any]:
    """Resolve a profile by username (dummy convenience helper)."""
    for profile in PROFILES:
        if profile["username"] == username:
            return profile
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")


@router.get("/{profile_id}")
async def get_profile(profile_id: str) -> dict[str, Any]:
    """Public artist profile (artist page header, artwork attribution)."""
    return _find_profile(profile_id)


@router.patch("/{profile_id}")
async def update_profile(profile_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Update profile display fields (dummy — returns the payload merged in)."""
    profile = _find_profile(profile_id)
    profile.update(payload)
    profile["updated_at"] = "2026-08-16T09:00:00Z"
    return profile


@router.get("/{profile_id}/artworks")
async def list_profile_artworks(
    profile_id: str,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """All artworks by one artist (artist page grid)."""
    _find_profile(profile_id)
    items = [a for a in ARTWORKS if a["profile_id"] == profile_id]
    return paginate(items, limit, offset)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_profile(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a profile (dummy — no persistence)."""
    return {
        "id": new_id(),
        "user_id": payload.get("user_id", new_id()),
        "username": payload.get("username", "artist"),
        "display_name": payload.get("display_name", "New Artist"),
        "bio": payload.get("bio"),
        "avatar_url": payload.get("avatar_url"),
        "cover_image_url": payload.get("cover_image_url"),
        "social_links": payload.get("social_links", {}),
        "created_at": "2026-08-16T09:00:00Z",
        "updated_at": "2026-08-16T09:00:00Z",
    }
