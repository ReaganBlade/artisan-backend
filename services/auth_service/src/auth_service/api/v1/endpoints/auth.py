from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.config import settings
from ....core.limiter import limiter
from ....db.session import get_db
from ....models import User
from ....schemas.token_schema import AuthResult, LogoutRequest, RefreshRequest
from ....schemas.user_schema import UserCreate, UserLogin, UserResponse
from ....services import auth_service
from ...v1.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=AuthResult,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.RATE_LIMIT_SIGNUP)
async def signup(
    request: Request,
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> AuthResult:
    """Create a new customer account and sign in immediately."""
    return await auth_service.signup(db, payload)


@router.post("/signin", response_model=AuthResult)
@limiter.limit(settings.RATE_LIMIT_SIGNIN)
async def signin(
    request: Request,
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> AuthResult:
    """Exchange email + password for an access/refresh token pair."""
    return await auth_service.signin(db, payload)


@router.post("/refresh", response_model=AuthResult)
@limiter.limit(settings.RATE_LIMIT_REFRESH)
async def refresh(
    request: Request,
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResult:
    """Rotate a refresh token and return a fresh token pair."""
    return await auth_service.refresh_tokens(db, payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(settings.RATE_LIMIT_LOGOUT)
async def logout(
    request: Request,
    payload: LogoutRequest,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Revoke the presented refresh token (idempotent)."""
    await auth_service.logout(db, payload.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse)
@limiter.limit(settings.RATE_LIMIT_ME)
async def me(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> User:
    """Return the profile of the currently authenticated user."""
    return current_user
