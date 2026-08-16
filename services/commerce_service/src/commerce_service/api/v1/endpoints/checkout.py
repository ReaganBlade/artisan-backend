"""Dummy Commerce Service endpoints for checkout and orders.

These mirror the real Stripe-backed flow: create a Checkout Session, poll its
status, and read back the resulting order. All responses are mocked.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status

from ..dummy_data import CART, ORDERS, new_id, cart_total

router = APIRouter(tags=["checkout", "orders"])


@router.post("/checkout", status_code=status.HTTP_201_CREATED)
async def create_checkout(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create a Stripe Checkout Session for the current cart (dummy).

    Returns a fake ``checkout_url`` the frontend would redirect the buyer to.
    """
    payload = payload or {}
    amount = payload.get("amount") or cart_total(CART)
    session_id = f"cs_test_{new_id().replace('-', '')}"
    return {
        "session_id": session_id,
        "checkout_url": f"https://checkout.stripe.example.com/c/pay/{session_id}",
        "amount": amount,
        "currency": payload.get("currency", "usd"),
        "status": "open",
    }


@router.get("/checkout/{session_id}")
async def get_checkout_status(session_id: str) -> dict[str, Any]:
    """Poll checkout session status (dummy — always completes)."""
    if not session_id.startswith("cs_test_"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Checkout session not found."
        )
    return {
        "session_id": session_id,
        "status": "complete",
        "payment_status": "paid",
        "order_id": new_id(),
    }


@router.post("/webhooks/stripe")
async def stripe_webhook(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Stripe webhook receiver (dummy — echo the event type back).

    In production this verifies the signature with ``STRIPE_WEBHOOK_SECRET`` and
    finalizes the order when ``checkout.session.completed`` arrives.
    """
    payload = payload or {}
    return {
        "received": True,
        "event_type": payload.get("type", "unknown"),
        "id": payload.get("id", new_id()),
    }


@router.get("/orders")
async def list_orders(
    buyer_id: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """List orders (order history / account page)."""
    items = [o for o in ORDERS if buyer_id is None or o["buyer_id"] == buyer_id]
    return {
        "items": items[offset : offset + limit],
        "total": len(items),
        "limit": limit,
        "offset": offset,
    }


@router.get("/orders/{order_id}")
async def get_order(order_id: str) -> dict[str, Any]:
    """Order detail with line items (order confirmation / receipt)."""
    for order in ORDERS:
        if order["id"] == order_id:
            return order
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
