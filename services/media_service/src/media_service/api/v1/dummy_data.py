"""Deterministic mock data for the Media Service dummy routes.

Every payload mirrors the shape of the SQLAlchemy models in
``media_service.models`` (artworks, media_files, profiles) so the frontend can
build against these routes and swap in real data with no contract changes.

NOTE: This module is a development aid only. Delete it (and the endpoints'
``dummy_`` helpers) once real persistence is implemented.
"""

from __future__ import annotations

import uuid
from typing import Any

# Fixed IDs so responses are stable across requests (useful for tests/UI).
PROFILE_IDS = {
    "mara": "11111111-1111-1111-1111-111111111101",
    "dex": "11111111-1111-1111-1111-111111111102",
    "ingrid": "11111111-1111-1111-1111-111111111103",
    "june": "11111111-1111-1111-1111-111111111104",
}

ARTWORK_IDS = [
    "22222222-2222-2222-2222-222222222201",
    "22222222-2222-2222-2222-222222222202",
    "22222222-2222-2222-2222-222222222203",
    "22222222-2222-2222-2222-222222222204",
    "22222222-2222-2222-2222-222222222205",
    "22222222-2222-2222-2222-222222222206",
    "22222222-2222-2222-2222-222222222207",
    "22222222-2222-2222-2222-222222222208",
]

_MEDIA_URL_BASE = "https://storage.example.com/artworks"

PROFILES: list[dict[str, Any]] = [
    {
        "id": PROFILE_IDS["mara"],
        "user_id": "33333333-3333-3333-3333-333333333301",
        "username": "mara",
        "display_name": "Mara Villanueva",
        "bio": "Printmaker. Screens, ink, and a lot of noise.",
        "avatar_url": f"{_MEDIA_URL_BASE}/avatars/mara.jpg",
        "cover_image_url": f"{_MEDIA_URL_BASE}/covers/mara.jpg",
        "social_links": {"instagram": "https://instagram.com/mara.prints"},
        "created_at": "2025-11-02T09:12:00Z",
        "updated_at": "2026-07-18T14:30:00Z",
    },
    {
        "id": PROFILE_IDS["dex"],
        "user_id": "33333333-3333-3333-3333-333333333302",
        "username": "dex",
        "display_name": "Dex Okafor",
        "bio": "Draws the city at 3am. Posters for rent.",
        "avatar_url": f"{_MEDIA_URL_BASE}/avatars/dex.jpg",
        "cover_image_url": f"{_MEDIA_URL_BASE}/covers/dex.jpg",
        "social_links": {"instagram": "https://instagram.com/dex.draws"},
        "created_at": "2025-12-19T18:05:00Z",
        "updated_at": "2026-08-02T10:11:00Z",
    },
    {
        "id": PROFILE_IDS["ingrid"],
        "user_id": "33333333-3333-3333-3333-333333333303",
        "username": "ingrid",
        "display_name": "Ingrid Sørensen",
        "bio": "Oil paintings about machines that miss you.",
        "avatar_url": f"{_MEDIA_URL_BASE}/avatars/ingrid.jpg",
        "cover_image_url": f"{_MEDIA_URL_BASE}/covers/ingrid.jpg",
        "social_links": {"website": "https://ingridsoerensen.example.com"},
        "created_at": "2025-09-30T08:00:00Z",
        "updated_at": "2026-07-30T16:45:00Z",
    },
    {
        "id": PROFILE_IDS["june"],
        "user_id": "33333333-3333-3333-3333-333333333304",
        "username": "june",
        "display_name": "June Park",
        "bio": "Carves anything that annoys her.",
        "avatar_url": f"{_MEDIA_URL_BASE}/avatars/june.jpg",
        "cover_image_url": f"{_MEDIA_URL_BASE}/covers/june.jpg",
        "social_links": {"tiktok": "https://tiktok.com/@june.carves"},
        "created_at": "2026-01-14T12:22:00Z",
        "updated_at": "2026-08-10T09:05:00Z",
    },
]

# (title, profile_id, art_type, price, status, description)
_ARTWORK_ROWS: list[tuple[str, str, str, float, str, str]] = [
    (
        "Sunshower",
        PROFILE_IDS["mara"],
        "Print",
        240.0,
        "published",
        "Screenprint on 300gsm cotton rag, signed and numbered.",
    ),
    (
        "Tape War",
        PROFILE_IDS["dex"],
        "Print",
        90.0,
        "published",
        "Risograph print, two colours, edition of 40.",
    ),
    (
        "Soft Machine",
        PROFILE_IDS["ingrid"],
        "Painting",
        510.0,
        "published",
        "Oil on panel, one of one.",
    ),
    (
        "Glass Teeth",
        PROFILE_IDS["june"],
        "Print",
        180.0,
        "published",
        "Linocut, edition of 30.",
    ),
    (
        "Parking Lot Sun",
        PROFILE_IDS["mara"],
        "Painting",
        320.0,
        "published",
        "Ink on paper, one of one.",
    ),
    (
        "Moth Season",
        PROFILE_IDS["june"],
        "Digital",
        145.0,
        "sold",
        "Digital print, edition of 50.",
    ),
    (
        "Heavy Metal",
        PROFILE_IDS["dex"],
        "Print",
        120.0,
        "published",
        "Screenprint, edition of 50.",
    ),
    (
        "Blue Noon",
        PROFILE_IDS["ingrid"],
        "Painting",
        460.0,
        "draft",
        "Oil on panel, one of one.",
    ),
]


def _artwork(row: tuple[str, str, str, float, str, str], artwork_id: str) -> dict[str, Any]:
    title, profile_id, art_type, price, status, description = row
    return {
        "id": artwork_id,
        "profile_id": profile_id,
        "title": title,
        "description": description,
        "art_type": art_type,
        "price": price,
        "status": status,
        "primary_media_url": f"{_MEDIA_URL_BASE}/{artwork_id}/primary.jpg",
        "created_at": "2026-06-01T10:00:00Z",
        "updated_at": "2026-08-01T10:00:00Z",
    }


ARTWORKS: list[dict[str, Any]] = [
    _artwork(row, artwork_id) for row, artwork_id in zip(_ARTWORK_ROWS, ARTWORK_IDS)
]

MEDIA_FILES: list[dict[str, Any]] = [
    {
        "id": "44444444-4444-4444-4444-444444444401",
        "artwork_id": ARTWORK_IDS[0],
        "file_url": f"{_MEDIA_URL_BASE}/{ARTWORK_IDS[0]}/01.jpg",
        "file_type": "image/jpeg",
        "file_size_bytes": 2_412_800,
        "display_order": 0,
        "created_at": "2026-06-01T10:05:00Z",
    },
    {
        "id": "44444444-4444-4444-4444-444444444402",
        "artwork_id": ARTWORK_IDS[0],
        "file_url": f"{_MEDIA_URL_BASE}/{ARTWORK_IDS[0]}/detail.jpg",
        "file_type": "image/jpeg",
        "file_size_bytes": 1_890_112,
        "display_order": 1,
        "created_at": "2026-06-01T10:06:00Z",
    },
    {
        "id": "44444444-4444-4444-4444-444444444403",
        "artwork_id": ARTWORK_IDS[1],
        "file_url": f"{_MEDIA_URL_BASE}/{ARTWORK_IDS[1]}/01.png",
        "file_type": "image/png",
        "file_size_bytes": 5_204_889,
        "display_order": 0,
        "created_at": "2026-06-02T09:00:00Z",
    },
]

STATUSES = ("draft", "pending", "published", "sold", "archived")
ART_TYPES = ("Painting", "Print", "Photography", "Digital", "Sculpture", "Ceramics")


def paginate(items: list[dict[str, Any]], limit: int, offset: int) -> dict[str, Any]:
    """Slice a list into the standard list-response envelope used by all services."""
    return {
        "items": items[offset : offset + limit],
        "total": len(items),
        "limit": limit,
        "offset": offset,
    }


def new_id() -> str:
    """Random v4 UUID string (used by the mutating dummy endpoints)."""
    return str(uuid.uuid4())
