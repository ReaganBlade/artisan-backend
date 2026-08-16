"""Dummy Moderation Service endpoints.

Mirrors the real flow: AI moderation tasks and the "Originality Engine"
signatures are enqueued per artwork, and human admins triage flags. All
responses are mocked.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status

from ..dummy_data import (
    ADMIN_REVIEW_FLAGS,
    ARTWORK_IDS,
    ARTWORK_SIGNATURES,
    MODERATION_TASKS,
    new_id,
)

router = APIRouter(tags=["moderation"])


def _task_for(artwork_id: str) -> dict[str, Any] | None:
    for task in MODERATION_TASKS:
        if task["artwork_id"] == artwork_id:
            return task
    return None


@router.post("/artworks/{artwork_id}/moderation", status_code=status.HTTP_201_CREATED)
async def submit_for_moderation(artwork_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Submit an artwork for AI moderation (dummy — returns a pending task)."""
    if artwork_id not in ARTWORK_IDS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Artwork not found."
        )
    payload = payload or {}
    return {
        "id": new_id(),
        "artwork_id": artwork_id,
        "task_type": payload.get("task_type", "image_safety"),
        "status": "pending",
        "result_payload": None,
        "error_message": None,
        "created_at": "2026-08-16T09:00:00Z",
        "updated_at": "2026-08-16T09:00:00Z",
    }


@router.get("/artworks/{artwork_id}/moderation")
async def get_moderation_status(artwork_id: str) -> dict[str, Any]:
    """Current moderation state of an artwork (status badge on the detail page)."""
    task = _task_for(artwork_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No moderation task found for this artwork.",
        )
    return task


@router.post("/artworks/{artwork_id}/signature", status_code=status.HTTP_201_CREATED)
async def register_signature(artwork_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Register an 'Originality Engine' perceptual hash for an artwork (dummy)."""
    if artwork_id not in ARTWORK_IDS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Artwork not found."
        )
    payload = payload or {}
    return {
        "id": new_id(),
        "artwork_id": artwork_id,
        "phash": payload.get("phash", "0000000000000000"),
        "created_at": "2026-08-16T09:00:00Z",
    }


@router.get("/artworks/{artwork_id}/signature")
async def get_signature(artwork_id: str) -> dict[str, Any]:
    """Look up an artwork's perceptual hash (duplicate/IP check)."""
    for signature in ARTWORK_SIGNATURES:
        if signature["artwork_id"] == artwork_id:
            return signature
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Signature not found."
    )


@router.get("/moderation/flags")
async def list_flags(
    status_filter: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """Admin queue of review flags (moderation dashboard)."""
    items = [
        f
        for f in ADMIN_REVIEW_FLAGS
        if status_filter is None or f["status"] == status_filter
    ]
    return {
        "items": items[offset : offset + limit],
        "total": len(items),
        "limit": limit,
        "offset": offset,
    }


@router.patch("/moderation/flags/{flag_id}")
async def resolve_flag(flag_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Triage a flag (approve/remove the artwork). Dummy — no persistence."""
    for flag in ADMIN_REVIEW_FLAGS:
        if flag["id"] == flag_id:
            flag["status"] = payload.get("status", "resolved")
            flag["reviewed_by"] = payload.get("reviewed_by")
            flag["updated_at"] = "2026-08-16T09:00:00Z"
            return flag
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flag not found.")
