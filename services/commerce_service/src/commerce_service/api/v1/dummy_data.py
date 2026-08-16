"""Deterministic mock data for the Commerce Service dummy routes.

Payloads mirror the shapes of the SQLAlchemy models in
``commerce_service.models`` (orders, order_items). The cart itself has no
dedicated table in the schema yet, so it is mocked as a client-side cart that
the checkout endpoint converts into an order — exactly how the real flow will
work once a cart/Stripe session is introduced.

NOTE: This module is a development aid only. Delete it once real persistence
(and Stripe) is implemented.
"""

from __future__ import annotations

import uuid
from typing import Any

BUYER_ID = "33333333-3333-3333-3333-333333333301"

# Fixed IDs so responses are stable across requests (useful for tests/UI).
ORDER_IDS = [
    "55555555-5555-5555-5555-555555555501",
    "55555555-5555-5555-5555-555555555502",
]

ARTWORK_IDS = [
    "22222222-2222-2222-2222-222222222201",  # Sunshower
    "22222222-2222-2222-2222-222222222202",  # Tape War
    "22222222-2222-2222-2222-222222222204",  # Glass Teeth
]

CART: dict[str, Any] = {
    "id": "66666666-6666-6666-6666-666666666601",
    "buyer_id": BUYER_ID,
    "items": [
        {
            "id": "77777777-7777-7777-7777-777777777701",
            "artwork_id": ARTWORK_IDS[0],
            "title": "Sunshower",
            "unit_price": 240.0,
            "quantity": 1,
        },
        {
            "id": "77777777-7777-7777-7777-777777777702",
            "artwork_id": ARTWORK_IDS[1],
            "title": "Tape War",
            "unit_price": 90.0,
            "quantity": 1,
        },
    ],
    "subtotal": 330.0,
    "currency": "usd",
}


def _order(order_id: str, *, paid: bool) -> dict[str, Any]:
    items: list[dict[str, Any]] = [
        {
            "id": f"{order_id}-item-1",
            "order_id": order_id,
            "artwork_id": ARTWORK_IDS[0],
            "title": "Sunshower",
            "price_at_purchase": 240.0,
            "quantity": 1,
        },
        {
            "id": f"{order_id}-item-2",
            "order_id": order_id,
            "artwork_id": ARTWORK_IDS[2],
            "title": "Glass Teeth",
            "price_at_purchase": 180.0,
            "quantity": 1,
        },
    ]
    total = sum(item["price_at_purchase"] * item["quantity"] for item in items)
    return {
        "id": order_id,
        "buyer_id": BUYER_ID,
        "total_amount": float(total),
        "payment_status": "paid" if paid else "pending",
        "fulfillment_status": "fulfilled" if paid else "processing",
        "stripe_session_id": f"cs_test_{order_id.replace('-', '')}",
        "items": items,
        "created_at": "2026-07-20T12:00:00Z",
        "updated_at": "2026-07-20T12:30:00Z",
    }


ORDERS: list[dict[str, Any]] = [
    _order(ORDER_IDS[0], paid=True),
    _order(ORDER_IDS[1], paid=False),
]


def cart_total(cart: dict[str, Any]) -> float:
    return round(
        sum(item["unit_price"] * item["quantity"] for item in cart["items"]), 2
    )


def new_id() -> str:
    """Random v4 UUID string (used by the mutating dummy endpoints)."""
    return str(uuid.uuid4())
