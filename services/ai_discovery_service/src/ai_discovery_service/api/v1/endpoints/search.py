"""Dummy AI Discovery Service endpoints for search.

The real implementation runs pgvector cosine search over ``artwork_embeddings``
and records every query in ``search_query_logs``. These stubs return the same
contract so the frontend search UI can be built against them.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from ..dummy_data import ARTWORK_IDS, _result, new_id, search_by_keyword

router = APIRouter(tags=["search"])


@router.get("/search")
async def search(
    q: str = Query("", description="Search text (title, medium, or artist)."),
    art_type: str | None = Query(None, description="Filter by art type."),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """Lexical keyword search over the catalog."""
    items = search_by_keyword(q)
    if art_type is not None:
        items = [i for i in items if i["art_type"] == art_type]
    return {
        "query": q,
        "is_semantic": False,
        "items": items[offset : offset + limit],
        "total": len(items),
        "limit": limit,
        "offset": offset,
    }


@router.post("/search/vibe")
async def vibe_search(payload: dict[str, Any]) -> dict[str, Any]:
    """Vibe / mood-based semantic search.

    ``payload``: ``{"query": "warm neon at dusk", "art_type": "Print", "limit": 12}``
    The dummy always returns the full mock catalog ordered by the fake score.
    """
    query = payload.get("query", "").strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="query is required.",
        )
    limit = payload.get("limit", 12)
    art_type = payload.get("art_type")
    items = [_result(i) for i in ARTWORK_IDS]
    if art_type is not None:
        items = [i for i in items if i["art_type"] == art_type]
    return {
        "query": query,
        "is_semantic": True,
        "items": items[:limit],
        "total": len(items),
        "limit": limit,
        "offset": 0,
    }


@router.get("/artworks/{artwork_id}/similar")
async def similar_artworks(
    artwork_id: str,
    limit: int = Query(8, ge=1, le=50),
) -> dict[str, Any]:
    """Artworks similar to a given artwork (embedding neighbors, mocked)."""
    if artwork_id not in ARTWORK_IDS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Artwork not found."
        )
    others = [i for i in ARTWORK_IDS if i != artwork_id]
    return {
        "artwork_id": artwork_id,
        "items": [_result(i) for i in others[:limit]],
        "total": len(others),
        "limit": limit,
    }


@router.post("/search/log")
async def log_search(payload: dict[str, Any]) -> dict[str, Any]:
    """Record a search query in the analytics log (dummy — no persistence)."""
    return {
        "id": new_id(),
        "user_id": payload.get("user_id"),
        "query_text": payload.get("query_text", ""),
        "is_semantic": payload.get("is_semantic", False),
        "result_count": payload.get("result_count", 0),
        "created_at": "2026-08-16T09:00:00Z",
    }
