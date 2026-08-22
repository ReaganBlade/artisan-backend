import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from ..models import User, UserRole
from ..repositories.refresh_token_repository import (
    create_refresh_token,
    get_refresh_token_by_hash,
    refresh_token_expiry,
    revoke_refresh_token,
)
from ..repositories.user_repository import (
    create_user,
    get_user_by_email,
)
from ..schemas.token_schema import AuthResult
from ..schemas.user_schema import UserCreate, UserLogin, UserResponse


def _normalize_email(email: str) -> str:
    """Emails are stored and compared in lowercase."""
    return email.strip().lower()


def _build_auth_result(user: User) -> AuthResult:
    return AuthResult(
        access_token=create_access_token(user.id),
        refresh_token=generate_refresh_token(),
        user=UserResponse.model_validate(user),
    )


async def _persist_refresh_token(
    db: AsyncSession, user_id: uuid.UUID, refresh_token: str
) -> None:
    await create_refresh_token(
        db,
        user_id=user_id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=refresh_token_expiry(settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


async def signup(db: AsyncSession, payload: UserCreate) -> AuthResult:
    """Register a new customer account and sign them in immediately."""
    email = _normalize_email(payload.email)

    if await get_user_by_email(db, email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = await create_user(
        db,
        email=email,
        hashed_password=hash_password(payload.password),
        role=UserRole.CUSTOMER,
    )

    result = _build_auth_result(user)
    await _persist_refresh_token(db, user.id, result.refresh_token)
    await db.commit()
    return result


async def signin(db: AsyncSession, payload: UserLogin) -> AuthResult:
    """Authenticate credentials and issue a fresh token pair."""
    email = _normalize_email(payload.email)
    user = await get_user_by_email(db, email)

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    result = _build_auth_result(user)
    await _persist_refresh_token(db, user.id, result.refresh_token)
    await db.commit()
    return result


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> AuthResult:
    """Rotate a valid refresh token: revoke the old one, issue a new pair."""
    stored = await get_refresh_token_by_hash(db, hash_refresh_token(refresh_token))

    if stored is None or stored.is_revoked or stored.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.get(User, stored.user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    await revoke_refresh_token(db, stored)
    result = _build_auth_result(user)
    await _persist_refresh_token(db, user.id, result.refresh_token)
    await db.commit()
    return result


async def logout(db: AsyncSession, refresh_token: str) -> None:
    """Revoke the presented refresh token. Idempotent — unknown tokens are ignored."""
    stored = await get_refresh_token_by_hash(db, hash_refresh_token(refresh_token))
    if stored is not None and not stored.is_revoked:
        await revoke_refresh_token(db, stored)
        await db.commit()
