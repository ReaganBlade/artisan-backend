import pytest
from fastapi import HTTPException

pytestmark = pytest.mark.usefixtures("_clean_tables_between_tests")
from sqlalchemy import select

from auth_service.core.security import (
    decode_access_token,
    hash_refresh_token,
    verify_password,
)
from auth_service.models import RefreshToken, User
from auth_service.repositories.user_repository import (
    get_refresh_token_by_hash,
    get_user_by_email,
)
from auth_service.schemas.user_schema import UserCreate, UserLogin
from auth_service.services import auth_service


def _create_payload(email="user@example.com", password="password123") -> UserCreate:
    return UserCreate(email=email, password=password)


class TestSignup:
    def test_creates_user_and_returns_token_pair(self, run_async):
        result = run_async(lambda db: auth_service.signup(db, _create_payload()))

        assert result.access_token
        assert result.refresh_token
        assert result.token_type == "bearer"
        assert result.user.email == "user@example.com"
        assert result.user.role.value == "CUSTOMER"

        # Access token identifies the same user.
        payload = decode_access_token(result.access_token)
        assert payload["sub"] == str(result.user.id)

        # User persisted with a verifiable password hash.
        user = run_async(lambda db: get_user_by_email(db, "user@example.com"))
        assert user is not None
        assert user.hashed_password != "password123"
        assert verify_password("password123", user.hashed_password)

        # Refresh token persisted as a hash, not revoked.
        stored = run_async(
            lambda db: get_refresh_token_by_hash(
                db, hash_refresh_token(result.refresh_token)
            )
        )
        assert stored is not None
        assert stored.user_id == result.user.id
        assert stored.is_revoked is False

    def test_normalizes_email_to_lowercase(self, run_async):
        result = run_async(
            lambda db: auth_service.signup(
                db, _create_payload(email="User@Example.COM")
            )
        )
        assert result.user.email == "user@example.com"

    def test_duplicate_email_raises_409(self, run_async):
        run_async(lambda db: auth_service.signup(db, _create_payload()))
        with pytest.raises(HTTPException) as exc_info:
            run_async(lambda db: auth_service.signup(db, _create_payload()))
        assert exc_info.value.status_code == 409


class TestSignin:
    def _signup(self, run_async, email="user@example.com", password="password123"):
        run_async(lambda db: auth_service.signup(db, _create_payload(email, password)))

    def test_valid_credentials_return_token_pair(self, run_async):
        self._signup(run_async)
        result = run_async(
            lambda db: auth_service.signin(
                db, UserLogin(email="user@example.com", password="password123")
            )
        )
        assert result.access_token
        assert result.refresh_token
        assert result.user.email == "user@example.com"

    def test_wrong_password_raises_401(self, run_async):
        self._signup(run_async)
        with pytest.raises(HTTPException) as exc_info:
            run_async(
                lambda db: auth_service.signin(
                    db, UserLogin(email="user@example.com", password="wrong-pass")
                )
            )
        assert exc_info.value.status_code == 401

    def test_unknown_email_raises_401(self, run_async):
        with pytest.raises(HTTPException) as exc_info:
            run_async(
                lambda db: auth_service.signin(
                    db, UserLogin(email="ghost@example.com", password="password123")
                )
            )
        assert exc_info.value.status_code == 401

    def test_deactivated_user_raises_403(self, run_async):
        result = run_async(lambda db: auth_service.signup(db, _create_payload()))

        async def deactivate(db):
            user = await db.get(User, result.user.id)
            user.is_active = False
            await db.commit()

        run_async(deactivate)
        with pytest.raises(HTTPException) as exc_info:
            run_async(
                lambda db: auth_service.signin(
                    db, UserLogin(email="user@example.com", password="password123")
                )
            )
        assert exc_info.value.status_code == 403


class TestRefresh:
    def test_rotates_token_and_revokes_old_one(self, run_async):
        signup_result = run_async(lambda db: auth_service.signup(db, _create_payload()))
        old_hash = hash_refresh_token(signup_result.refresh_token)

        refreshed = run_async(
            lambda db: auth_service.refresh_tokens(db, signup_result.refresh_token)
        )
        assert refreshed.access_token
        assert refreshed.refresh_token != signup_result.refresh_token
        assert refreshed.user.id == signup_result.user.id

        # Old token is now revoked; new token works for another rotation.
        old_stored = run_async(
            lambda db: get_refresh_token_by_hash(db, old_hash)
        )
        assert old_stored.is_revoked is True

        again = run_async(
            lambda db: auth_service.refresh_tokens(db, refreshed.refresh_token)
        )
        assert again.refresh_token != refreshed.refresh_token

    def test_unknown_token_raises_401(self, run_async):
        with pytest.raises(HTTPException) as exc_info:
            run_async(lambda db: auth_service.refresh_tokens(db, "bogus-token"))
        assert exc_info.value.status_code == 401

    def test_revoked_token_raises_401(self, run_async):
        signup_result = run_async(lambda db: auth_service.signup(db, _create_payload()))
        run_async(lambda db: auth_service.logout(db, signup_result.refresh_token))

        with pytest.raises(HTTPException) as exc_info:
            run_async(
                lambda db: auth_service.refresh_tokens(db, signup_result.refresh_token)
            )
        assert exc_info.value.status_code == 401


class TestLogout:
    def test_revokes_token(self, run_async):
        signup_result = run_async(lambda db: auth_service.signup(db, _create_payload()))
        run_async(lambda db: auth_service.logout(db, signup_result.refresh_token))

        stored = run_async(
            lambda db: get_refresh_token_by_hash(
                db, hash_refresh_token(signup_result.refresh_token)
            )
        )
        assert stored.is_revoked is True

    def test_logout_is_idempotent(self, run_async):
        signup_result = run_async(lambda db: auth_service.signup(db, _create_payload()))
        run_async(lambda db: auth_service.logout(db, signup_result.refresh_token))
        # Second logout must not raise.
        run_async(lambda db: auth_service.logout(db, signup_result.refresh_token))

    def test_logout_with_unknown_token_is_noop(self, run_async):
        run_async(lambda db: auth_service.logout(db, "bogus-token"))
