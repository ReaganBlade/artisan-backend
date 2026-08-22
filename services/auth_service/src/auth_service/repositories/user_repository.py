import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User, UserRole


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


async def update_user(
    db: AsyncSession,
    user: User,
    **fields: object,
) -> User:
    """Apply the given field updates to an existing user and flush."""
    for key, value in fields.items():
        if value is not None and hasattr(user, key):
            setattr(user, key, value)
    await db.flush()
    return user

