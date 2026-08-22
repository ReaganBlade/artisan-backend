"""Persistence operations for refresh tokens."""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import RefreshToken


def refresh_token_expiry(days: int) -> datetime:
    """Expiry timestamp for a refresh token, `days` from now (UTC, aware)."""
    return datetime.now(timezone.utc) + timedelta(days=days)


async def create_refresh_token(
    db: AsyncSession,
    user_id: uuid.UUID,
    token_hash: str,
    expires_at: datetime,
) -> RefreshToken:
    """Persist a new refresh-token record."""
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token_hash,
        expires_at=expires_at,
    )
    db.add(refresh_token)
    await db.flush()
    return refresh_token


async def get_refresh_token_by_hash(
    db: AsyncSession, token_hash: str
) -> RefreshToken | None:
    """Look up a refresh token by its SHA-256 digest."""
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == token_hash)
    )
    return result.scalar_one_or_none()


async def revoke_refresh_token(db: AsyncSession, refresh_token: RefreshToken) -> None:
    """Mark a refresh token as revoked."""
    refresh_token.is_revoked = True
    await db.flush()
