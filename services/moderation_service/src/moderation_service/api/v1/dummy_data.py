"""Deterministic mock data for the Moderation Service dummy routes.

Payloads mirror the shapes of the SQLAlchemy models in
``moderation_service.models`` (moderation_tasks, admin_review_flags,
artwork_signatures).
"""

from __future__ import annotations

import uuid
from typing import Any

ARTWORK_IDS = [
    "22222222-2222-2222-2222-222222222201",  # Sunshower
    "22222222-2222-2222-2222-222222222202",  # Tape War
    "22222222-2222-2222-2222-222222222203",  # Soft Machine
    "22222222-2222-2222-2222-222222222204",  # Glass Teeth
    "22222222-2222-2222-2222-222222222206",  # Moth Season
]

MODERATION_TASKS: list[dict[str, Any]] = [
    {
        "id": "88888888-8888-8888-8888-888888888801",
        "artwork_id": ARTWORK_IDS[0],
        "task_type": "image_safety",
        "status": "approved",
        "result_payload": {"safe": True, "label": "artwork", "confidence": 0.98},
        "error_message": None,
        "created_at": "2026-07-01T08:00:00Z",
        "updated_at": "2026-07-01T08:00:05Z",
    },
    {
        "id": "88888888-8888-8888-8888-888888888802",
        "artwork_id": ARTWORK_IDS[1],
        "task_type": "image_safety",
        "status": "pending",
        "result_payload": None,
        "error_message": None,
        "created_at": "2026-08-10T11:30:00Z",
        "updated_at": "2026-08-10T11:30:00Z",
    },
    {
        "id": "88888888-8888-8888-8888-888888888803",
        "artwork_id": ARTWORK_IDS[4],
        "task_type": "image_safety",
        "status": "flagged",
        "result_payload": {"safe": False, "label": "suspected_copyright", "confidence": 0.84},
        "error_message": None,
        "created_at": "2026-08-12T14:00:00Z",
        "updated_at": "2026-08-12T14:00:04Z",
    },
]

ADMIN_REVIEW_FLAGS: list[dict[str, Any]] = [
    {
        "id": "99999999-9999-9999-9999-999999999901",
        "artwork_id": ARTWORK_IDS[4],
        "flag_reason": "suspected_copyright",
        "severity_score": 0.84,
        "status": "open",
        "reviewed_by": None,
        "created_at": "2026-08-12T14:00:05Z",
        "updated_at": "2026-08-12T14:00:05Z",
    },
    {
        "id": "99999999-9999-9999-9999-999999999902",
        "artwork_id": ARTWORK_IDS[2],
        "flag_reason": "user_report",
        "severity_score": 0.42,
        "status": "resolved",
        "reviewed_by": "33333333-3333-3333-3333-333333333305",
        "created_at": "2026-07-22T10:00:00Z",
        "updated_at": "2026-07-23T09:15:00Z",
    },
]

ARTWORK_SIGNATURES: list[dict[str, Any]] = [
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1",
        "artwork_id": ARTWORK_IDS[0],
        "phash": "a1b2c3d4e5f60718",
        "created_at": "2026-07-01T08:00:06Z",
    },
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2",
        "artwork_id": ARTWORK_IDS[1],
        "phash": "f0e1d2c3b4a59687",
        "created_at": "2026-08-10T11:30:01Z",
    },
]


def new_id() -> str:
    """Random v4 UUID string (used by the mutating dummy endpoints)."""
    return str(uuid.uuid4())
