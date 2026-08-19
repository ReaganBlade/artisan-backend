"""Business-logic / repository layer for Profile CRUD."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.profiles import Profile
from ..schemas.profile_schemas import ProfileCreate, ProfileUpdate


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------


async def get_profile_by_id(
    db: AsyncSession,
    profile_id: uuid.UUID,
) -> Profile | None:
    """Return a single profile by its PK, or ``None``."""
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    return result.scalar_one_or_none()


async def get_profile_by_user_id(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> Profile | None:
    """Return the profile linked to an auth user, or ``None``."""
    result = await db.execute(select(Profile).where(Profile.user_id == user_id))
    return result.scalar_one_or_none()


async def get_profile_by_username(
    db: AsyncSession,
    username: str,
) -> Profile | None:
    """Return a profile by its unique username handle."""
    result = await db.execute(select(Profile).where(Profile.username == username))
    return result.scalar_one_or_none()


async def list_profiles(
    db: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Profile], int]:
    """Return a page of profiles and the total count."""
    # Total count
    from sqlalchemy import func

    total_q = await db.execute(select(func.count(Profile.id)))
    total: int = total_q.scalar_one()  # type: ignore[assignment]

    # Page
    result = await db.execute(
        select(Profile).order_by(Profile.created_at.desc()).offset(offset).limit(limit)
    )
    profiles = list(result.scalars().all())
    return profiles, total


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


async def create_profile(
    db: AsyncSession,
    payload: ProfileCreate,
) -> Profile:
    """Persist a new profile and return it."""
    profile = Profile(**payload.model_dump())
    db.add(profile)
    await db.flush()
    await db.refresh(profile)
    return profile


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


async def update_profile(
    db: AsyncSession,
    profile: Profile,
    payload: ProfileUpdate,
) -> Profile:
    """Apply partial updates to an existing profile."""
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    await db.flush()
    await db.refresh(profile)
    return profile


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


async def delete_profile(
    db: AsyncSession,
    profile: Profile,
) -> None:
    """Soft-delete is not supported — hard delete."""
    await db.delete(profile)
    await db.flush()
