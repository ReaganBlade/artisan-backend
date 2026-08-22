"""Business logic for user profile operations."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from ..repositories.user_repository import get_user_by_id, update_user
from ..schemas.user_schema import UserUpdate


async def get_user(db: AsyncSession, user_id: uuid.UUID) -> User:
    """Fetch a user by ID or raise 404."""
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user


async def update_user_profile(
    db: AsyncSession, user_id: uuid.UUID, payload: UserUpdate
) -> User:
    """Apply partial updates to a user's profile."""
    user = await get_user(db, user_id)

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return user

    # If email is changing, check for conflicts.
    if "email" in updates:
        from ..repositories.user_repository import get_user_by_email

        existing = await get_user_by_email(db, updates["email"])
        if existing is not None and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

    return await update_user(db, user, **updates)
