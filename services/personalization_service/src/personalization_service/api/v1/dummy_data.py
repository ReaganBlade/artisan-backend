"""Deterministic mock data for the Personalization Service dummy routes.

Payloads mirror the shapes of the SQLAlchemy models in
``personalization_service.models`` (user_interactions, personalized_feed_cache).
"""

from __future__ import annotations

import uuid
from typing import Any

USER_ID = "33333333-3333-3333-3333-333333333301"

ARTWORK_IDS = [
    "22222222-2222-2222-2222-222222222201",  # Sunshower
    "22222222-2222-2222-2222-222222222202",  # Tape War
    "22222222-2222-2222-2222-222222222203",  # Soft Machine
    "22222222-2222-2222-2222-222222222204",  # Glass Teeth
    "22222222-2222-2222-2222-222222222205",  # Parking Lot Sun
    "22222222-2222-2222-2222-222222222207",  # Heavy Metal
]

# (artwork_id, title, art_type, price, artist)
_FEED_ROWS: list[tuple[str, str, str, float, str]] = [
    (ARTWORK_IDS[4], "Parking Lot Sun", "Painting", 320.0, "Mara Villanueva"),
    (ARTWORK_IDS[0], "Sunshower", "Print", 240.0, "Mara Villanueva"),
    (ARTWORK_IDS[2], "Soft Machine", "Painting", 510.0, "Ingrid Sørensen"),
    (ARTWORK_IDS[3], "Glass Teeth", "Print", 180.0, "June Park"),
    (ARTWORK_IDS[1], "Tape War", "Print", 90.0, "Dex Okafor"),
    (ARTWORK_IDS[5], "Heavy Metal", "Print", 120.0, "Dex Okafor"),
]

# Personalized feed cache (1:1 per user) — an ordered list of artwork ids.
FEED_CACHE: dict[str, Any] = {
    "user_id": USER_ID,
    "cached_artwork_ids": ARTWORK_IDS,
    "last_calculated_at": "2026-08-15T06:00:00Z",
}

INTERACTIONS: list[dict[str, Any]] = [
    {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbb01",
        "user_id": USER_ID,
        "artwork_id": ARTWORK_IDS[0],
        "interaction_type": "like",
        "created_at": "2026-08-10T12:00:00Z",
    },
    {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbb02",
        "user_id": USER_ID,
        "artwork_id": ARTWORK_IDS[4],
        "interaction_type": "view",
        "created_at": "2026-08-11T18:22:00Z",
    },
    {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbb03",
        "user_id": USER_ID,
        "artwork_id": ARTWORK_IDS[2],
        "interaction_type": "follow_artist",
        "created_at": "2026-08-12T09:45:00Z",
    },
]

INTERACTION_TYPES = ("like", "view", "follow_artist", "save", "share")


def feed_result(artwork_id: str) -> dict[str, Any]:
    for row in _FEED_ROWS:
        if row[0] == artwork_id:
            _, title, art_type, price, artist = row
            return {
                "artwork_id": artwork_id,
                "title": title,
                "art_type": art_type,
                "price": price,
                "artist": artist,
                "status": "published",
            }
    raise KeyError(artwork_id)


def new_id() -> str:
    """Random v4 UUID string (used by the mutating dummy endpoints)."""
    return str(uuid.uuid4())
