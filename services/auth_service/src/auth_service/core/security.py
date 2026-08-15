import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import settings


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------
# bcrypt is used directly rather than through passlib: passlib 1.7.4 breaks
# with bcrypt >= 4.1 ("error reading bcrypt version"). bcrypt 5.x also rejects
# passwords longer than 72 bytes, so schema validation caps length at 72.
def hash_password(password: str) -> str:
    """Hash a plaintext password with a per-user salt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True when `plain` matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Access tokens (JWT)
# ---------------------------------------------------------------------------
def create_access_token(user_id: uuid.UUID) -> str:
    """Issue a short-lived JWT carrying the user's id in `sub`."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decode and validate an access token, or return None when invalid/expired."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        return None
    # Only access tokens may be used for bearer authentication.
    if payload.get("type") != "access":
        return None
    return payload


# ---------------------------------------------------------------------------
# Refresh tokens (stateful, opaque)
# ---------------------------------------------------------------------------
def generate_refresh_token() -> str:
    """Generate a cryptographically random opaque refresh token."""
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    """SHA-256 digest of a refresh token — only the digest is persisted."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
