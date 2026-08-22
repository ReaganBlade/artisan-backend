"""User profile endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.config import settings
from ....core.limiter import limiter
from ....db.session import get_db
from ....models import User
from ....schemas.user_schema import UserResponse, UserUpdate
from ....services import user_service
from ...v1.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
@limiter.limit(settings.RATE_LIMIT_ME)
async def me(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> User:
    """Return the profile of the currently authenticated user."""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
@limiter.limit(settings.RATE_LIMIT_ME)
async def get_user(
    request: Request,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> User:
    """Fetch a user's public profile by ID."""
    return await user_service.get_user(db, user_id)


@router.patch("/{user_id}", response_model=UserResponse)
@limiter.limit(settings.RATE_LIMIT_ME)
async def patch_user(
    request: Request,
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    """Update a user's profile.  Users may only update their own profile."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile.",
        )
    return await user_service.update_user_profile(db, user_id, payload)
