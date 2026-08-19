"""Shared FastAPI dependencies used across all v1 endpoints."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async SQLAlchemy session scoped to the request lifecycle."""
    async with AsyncSessionLocal() as session:
        yield session
