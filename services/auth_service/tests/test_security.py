import uuid
from datetime import datetime, timedelta, timezone

import jwt

from auth_service.core.config import settings
from auth_service.core.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


class TestPasswords:
    def test_hash_and_verify_roundtrip(self):
        hashed = hash_password("s3cret-pass")
        assert hashed != "s3cret-pass"
        assert verify_password("s3cret-pass", hashed)

    def test_verify_rejects_wrong_password(self):
        hashed = hash_password("correct-pass")
        assert not verify_password("wrong-pass", hashed)

    def test_verify_rejects_malformed_hash(self):
        assert not verify_password("anything", "not-a-bcrypt-hash")

    def test_hashes_are_salted(self):
        assert hash_password("same-pass") != hash_password("same-pass")


class TestAccessTokens:
    def test_create_and_decode_roundtrip(self):
        user_id = uuid.uuid4()
        token = create_access_token(user_id)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

    def test_decode_rejects_garbage(self):
        assert decode_access_token("not.a.jwt") is None

    def test_decode_rejects_token_signed_with_other_key(self):
        payload = {
            "sub": str(uuid.uuid4()),
            "type": "access",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        }
        token = jwt.encode(
            payload, "some-other-secret-key-that-is-long-enough-32b", algorithm="HS256"
        )
        assert decode_access_token(token) is None

    def test_decode_rejects_expired_token(self):
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(uuid.uuid4()),
            "type": "access",
            "iat": now - timedelta(hours=2),
            "exp": now - timedelta(hours=1),
        }
        token = jwt.encode(
            payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        assert decode_access_token(token) is None

    def test_decode_rejects_non_access_token_type(self):
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(uuid.uuid4()),
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=30),
        }
        token = jwt.encode(
            payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        assert decode_access_token(token) is None


class TestRefreshTokens:
    def test_generate_produces_long_opaque_unique_tokens(self):
        a, b = generate_refresh_token(), generate_refresh_token()
        assert a != b
        assert len(a) > 40
        assert a != hash_refresh_token(a)

    def test_hash_is_deterministic_sha256(self):
        token = generate_refresh_token()
        assert hash_refresh_token(token) == hash_refresh_token(token)
        assert len(hash_refresh_token(token)) == 64
