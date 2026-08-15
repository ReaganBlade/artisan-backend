from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

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
async def signup(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> AuthResult:
    """Create a new customer account and sign in immediately."""
    return await auth_service.signup(db, payload)


@router.post("/signin", response_model=AuthResult)
async def signin(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> AuthResult:
    """Exchange email + password for an access/refresh token pair."""
    return await auth_service.signin(db, payload)


@router.post("/refresh", response_model=AuthResult)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResult:
    """Rotate a refresh token and return a fresh token pair."""
    return await auth_service.refresh_tokens(db, payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: LogoutRequest,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Revoke the presented refresh token (idempotent)."""
    await auth_service.logout(db, payload.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> User:
    """Return the profile of the currently authenticated user."""
    return current_user
