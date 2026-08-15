from pydantic import BaseModel, Field

from .user_schema import UserResponse


class TokenPair(BaseModel):
    """Access + refresh token issued on signup/signin/refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResult(TokenPair):
    """Token pair bundled with the authenticated user."""

    user: UserResponse


class RefreshRequest(BaseModel):
    """Payload for POST /auth/refresh — the token to rotate."""

    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    """Payload for POST /auth/logout — the token to revoke."""

    refresh_token: str = Field(min_length=1)
