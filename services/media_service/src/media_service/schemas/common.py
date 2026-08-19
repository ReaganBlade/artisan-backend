"""Shared Pydantic schemas used across entities."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Standard pagination query parameters."""

    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ListResponse(BaseModel):
    """Generic paginated list envelope."""

    items: list[dict]  # concrete items typed per endpoint
    total: int
    limit: int
    offset: int
