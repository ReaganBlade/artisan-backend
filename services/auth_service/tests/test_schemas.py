import pytest
from pydantic import ValidationError

from auth_service.schemas.token_schema import LogoutRequest, RefreshRequest
from auth_service.schemas.user_schema import UserCreate, UserLogin


class TestUserCreate:
    def test_valid(self):
        user = UserCreate(email="user@example.com", password="password123")
        assert user.email == "user@example.com"
        assert user.password == "password123"

    @pytest.mark.parametrize("email", ["not-an-email", "missing-tld@example", "a@b"])
    def test_invalid_email_raises(self, email):
        with pytest.raises(ValidationError):
            UserCreate(email=email, password="password123")

    def test_password_too_short_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(email="user@example.com", password="short")

    def test_password_too_long_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(email="user@example.com", password="x" * 73)


class TestUserLogin:
    def test_valid(self):
        login = UserLogin(email="user@example.com", password="whatever")
        assert login.email == "user@example.com"

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            UserLogin(email="nope", password="whatever")


class TestTokenRequests:
    def test_refresh_request_valid(self):
        assert RefreshRequest(refresh_token="abc").refresh_token == "abc"

    def test_refresh_request_empty_token_raises(self):
        with pytest.raises(ValidationError):
            RefreshRequest(refresh_token="")

    def test_logout_request_valid(self):
        assert LogoutRequest(refresh_token="abc").refresh_token == "abc"

    def test_logout_request_empty_token_raises(self):
        with pytest.raises(ValidationError):
            LogoutRequest(refresh_token="")
