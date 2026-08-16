"""Deterministic mock data for the AI Discovery Service dummy routes.

Search results embed a lightweight artwork summary. Full artwork records live
behind the Media Service; the discovery service only returns what is needed to
render a result grid, exactly as the real pgvector-backed implementation will.
"""

from __future__ import annotations

import uuid
from typing import Any

ARTWORK_IDS = [
    "22222222-2222-2222-2222-222222222201",  # Sunshower
    "22222222-2222-2222-2222-222222222202",  # Tape War
    "22222222-2222-2222-2222-222222222203",  # Soft Machine
    "22222222-2222-2222-2222-222222222204",  # Glass Teeth
    "22222222-2222-2222-2222-222222222205",  # Parking Lot Sun
    "22222222-2222-2222-2222-222222222207",  # Heavy Metal
]

# (artwork_id, title, art_type, price, status, profile_display_name)
_SEARCH_INDEX: list[tuple[str, str, str, float, str, str]] = [
    (ARTWORK_IDS[0], "Sunshower", "Print", 240.0, "published", "Mara Villanueva"),
    (ARTWORK_IDS[1], "Tape War", "Print", 90.0, "published", "Dex Okafor"),
    (ARTWORK_IDS[2], "Soft Machine", "Painting", 510.0, "published", "Ingrid Sørensen"),
    (ARTWORK_IDS[3], "Glass Teeth", "Print", 180.0, "published", "June Park"),
    (ARTWORK_IDS[4], "Parking Lot Sun", "Painting", 320.0, "published", "Mara Villanueva"),
    (ARTWORK_IDS[5], "Heavy Metal", "Print", 120.0, "published", "Dex Okafor"),
]

# Keyword -> artwork ids, used to fake lexical search.
_KEYWORD_MAP: dict[str, list[str]] = {
    "sun": [ARTWORK_IDS[0], ARTWORK_IDS[4]],
    "print": [ARTWORK_IDS[0], ARTWORK_IDS[1], ARTWORK_IDS[3], ARTWORK_IDS[5]],
    "painting": [ARTWORK_IDS[2], ARTWORK_IDS[4]],
    "metal": [ARTWORK_IDS[5]],
    "machine": [ARTWORK_IDS[2]],
}


def _result(artwork_id: str) -> dict[str, Any]:
    for row in _SEARCH_INDEX:
        if row[0] == artwork_id:
            _, title, art_type, price, status, artist = row
            return {
                "artwork_id": artwork_id,
                "title": title,
                "art_type": art_type,
                "price": price,
                "status": status,
                "artist": artist,
                "score": 0.91,  # cosine similarity, mocked
            }
    raise KeyError(artwork_id)


def search_by_keyword(query: str) -> list[dict[str, Any]]:
    """Fake lexical search: match against title and art_type substrings."""
    lowered = query.lower().strip()
    if not lowered:
        return [_result(i) for i in ARTWORK_IDS]
    matches: list[dict[str, Any]] = []
    for row in _SEARCH_INDEX:
        _, title, art_type, _, status, artist = row
        if lowered in title.lower() or lowered in art_type.lower() or lowered in artist.lower():
            matches.append(_result(row[0]))
    # Fall back to the keyword map for synonyms ("vibe terms").
    for keyword, ids in _KEYWORD_MAP.items():
        if lowered in keyword:
            for artwork_id in ids:
                result = _result(artwork_id)
                if result not in matches:
                    matches.append(result)
    return matches


def new_id() -> str:
    """Random v4 UUID string (used by the mutating dummy endpoints)."""
    return str(uuid.uuid4())
