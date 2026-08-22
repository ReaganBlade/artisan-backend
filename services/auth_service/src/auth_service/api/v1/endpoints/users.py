"""User profile and gateway-facing auth endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.config import settings
from ....core.limiter import limiter
from ....db.session import get_db
from ....models import User
from ....models.user_role import UserRole
from ....schemas.token_schema import AuthResult
from ....schemas.user_schema import UserCreate, UserLogin, UserResponse, UserUpdate
from ....services import auth_service, user_service
from ...v1.dependencies import get_current_user, require_role

router = APIRouter(prefix="/users", tags=["users"])


# ---------------------------------------------------------------------------
# Gateway contract: POST /users/register · POST /users/login
# ---------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=AuthResult,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.RATE_LIMIT_SIGNUP)
async def register(
    request: Request,
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> AuthResult:
    """Register a new account and sign in immediately (gateway contract)."""
    return await auth_service.signup(db, payload)


@router.post("/login", response_model=AuthResult)
@limiter.limit(settings.RATE_LIMIT_SIGNIN)
async def login(
    request: Request,
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> AuthResult:
    """Exchange email + password for a token pair (gateway contract)."""
    return await auth_service.signin(db, payload)


# ---------------------------------------------------------------------------
# Protected user-management routes
# ---------------------------------------------------------------------------

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


@router.get("/admin/list", response_model=list[UserResponse])
@limiter.limit(settings.RATE_LIMIT_ME)
async def list_users_admin(
    request: Request,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> list[User]:
    """List all users (admin only)."""
    from ....repositories.user_repository import list_all_users

    return await list_all_users(db)
