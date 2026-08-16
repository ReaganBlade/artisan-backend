import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.security import decode_access_token
from ...db.session import get_db
from ...models import User
from ...repositories.user_repository import get_user_by_id

bearer_scheme = HTTPBearer(auto_error=False)

_UNAUTHORIZED = {
    "status_code": status.HTTP_401_UNAUTHORIZED,
    "headers": {"WWW-Authenticate": "Bearer"},
}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db), 
) -> User:
    """Resolve the authenticated user from the Bearer access token."""
    if credentials is None:
        raise HTTPException(
            detail="Not authenticated.",
            **_UNAUTHORIZED,
        )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            detail="Invalid or expired access token.",
            **_UNAUTHORIZED,
        )

    user = await get_user_by_id(db, uuid.UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(
            detail="Invalid or expired access token.",
            **_UNAUTHORIZED,
        )
    return user
