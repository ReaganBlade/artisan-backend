"""Dummy Commerce Service endpoints for the shopping cart.

There is no cart table in the schema yet, so these endpoints operate on an
in-memory mock cart. The real implementation will back the cart with a Stripe
Checkout Session or a dedicated cart table.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status

from ..dummy_data import CART, cart_total, new_id

router = APIRouter(prefix="/cart", tags=["cart"])


def _find_item(item_id: str) -> dict[str, Any]:
    for item in CART["items"]:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found.")


@router.get("")
async def get_cart() -> dict[str, Any]:
    """Current cart with line items and subtotal (cart drawer / checkout page)."""
    CART["subtotal"] = cart_total(CART)
    return CART


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def add_cart_item(payload: dict[str, Any]) -> dict[str, Any]:
    """Add an artwork to the cart (dummy — no persistence)."""
    if not payload.get("artwork_id"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="artwork_id is required.",
        )
    item = {
        "id": new_id(),
        "artwork_id": payload["artwork_id"],
        "title": payload.get("title", "Untitled"),
        "unit_price": payload.get("unit_price", 0.0),
        "quantity": payload.get("quantity", 1),
    }
    CART["items"].append(item)
    CART["subtotal"] = cart_total(CART)
    return item


@router.patch("/items/{item_id}")
async def update_cart_item(item_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Update the quantity of a cart line item."""
    item = _find_item(item_id)
    quantity = payload.get("quantity")
    if quantity is not None:
        if quantity < 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="quantity must be at least 1.",
            )
        item["quantity"] = quantity
    CART["subtotal"] = cart_total(CART)
    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_cart_item(item_id: str) -> None:
    """Remove a line item from the cart."""
    _find_item(item_id)
    CART["items"] = [i for i in CART["items"] if i["id"] != item_id]
    CART["subtotal"] = cart_total(CART)
    return None


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart() -> None:
    """Empty the cart."""
    CART["items"].clear()
    CART["subtotal"] = 0.0
    return None
