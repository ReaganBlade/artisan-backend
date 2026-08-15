import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import RefreshToken, User, UserRole


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await db.get(User, user_id)


async def create_user(
    db: AsyncSession,
    email: str,
    hashed_password: str,
    role: UserRole = UserRole.CUSTOMER,
) -> User:
    user = User(email=email, hashed_password=hashed_password, role=role)
    db.add(user)
    await db.flush()
    return user


# ---------------------------------------------------------------------------
# Refresh tokens
# ---------------------------------------------------------------------------
def refresh_token_expiry(days: int) -> datetime:
    """Expiry timestamp for a refresh token, `days` from now (UTC, aware)."""
    return datetime.now(timezone.utc) + timedelta(days=days)


async def create_refresh_token(
    db: AsyncSession,
    user_id: uuid.UUID,
    token_hash: str,
    expires_at: datetime,
) -> RefreshToken:
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
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == token_hash)
    )
    return result.scalar_one_or_none()


async def revoke_refresh_token(db: AsyncSession, refresh_token: RefreshToken) -> None:
    refresh_token.is_revoked = True
    await db.flush()
