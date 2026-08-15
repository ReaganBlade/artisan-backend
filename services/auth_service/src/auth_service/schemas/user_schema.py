import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..models.user_role import UserRole

# Lightweight email check (avoids pulling in email-validator as a dependency).
EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class UserBase(BaseModel):
    """Fields shared across user schemas."""

    email: str = Field(pattern=EMAIL_PATTERN)


class UserCreate(UserBase):
    """Payload for POST /auth/signup."""

    # bcrypt 5.x rejects passwords over 72 bytes.
    password: str = Field(min_length=8, max_length=72)


class UserLogin(UserBase):
    """Payload for POST /auth/signin."""

    password: str = Field(min_length=1, max_length=72)


class UserResponse(UserBase):
    """User representation returned to clients — never includes the hash."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: UserRole
    is_active: bool
    created_at: datetime
