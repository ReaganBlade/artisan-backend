import pytest
from sqlalchemy import select

from auth_service.models import User

pytestmark = pytest.mark.usefixtures("_clean_tables_between_tests")

SIGNUP_URL = "/api/v1/auth/signup"
SIGNIN_URL = "/api/v1/auth/signin"
REFRESH_URL = "/api/v1/auth/refresh"
LOGOUT_URL = "/api/v1/auth/logout"
ME_URL = "/api/v1/auth/me"


def _signup_payload(email="user@example.com", password="password123"):
    return {"email": email, "password": password}


class TestSignupEndpoint:
    def test_signup_returns_201_with_token_pair(self, client):
        resp = client.post(SIGNUP_URL, json=_signup_payload())
        assert resp.status_code == 201

        body = resp.json()
        assert body["access_token"]
        assert body["refresh_token"]
        assert body["token_type"] == "bearer"
        assert body["user"]["email"] == "user@example.com"
        assert body["user"]["role"] == "CUSTOMER"
        assert "hashed_password" not in body["user"]

    def test_duplicate_email_returns_409(self, client):
        client.post(SIGNUP_URL, json=_signup_payload())
        resp = client.post(SIGNUP_URL, json=_signup_payload())
        assert resp.status_code == 409

    @pytest.mark.parametrize(
        "payload",
        [
            {"email": "not-an-email", "password": "password123"},
            {"email": "user@example.com", "password": "short"},
        ],
    )
    def test_invalid_payload_returns_422(self, client, payload):
        resp = client.post(SIGNUP_URL, json=payload)
        assert resp.status_code == 422


class TestSigninEndpoint:
    def _signup(self, client):
        client.post(SIGNUP_URL, json=_signup_payload())

    def test_valid_credentials_return_200(self, client):
        self._signup(client)
        resp = client.post(
            SIGNIN_URL, json=_signup_payload()
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["access_token"]
        assert body["refresh_token"]
        assert body["user"]["email"] == "user@example.com"

    def test_wrong_password_returns_401(self, client):
        self._signup(client)
        resp = client.post(
            SIGNIN_URL,
            json={"email": "user@example.com", "password": "wrong-pass"},
        )
        assert resp.status_code == 401


class TestRefreshEndpoint:
    def _signup(self, client):
        return client.post(SIGNUP_URL, json=_signup_payload()).json()

    def test_refresh_rotates_token(self, client):
        signup = self._signup(client)
        resp = client.post(REFRESH_URL, json={"refresh_token": signup["refresh_token"]})
        assert resp.status_code == 200
        body = resp.json()
        assert body["access_token"]
        assert body["refresh_token"] != signup["refresh_token"]

    def test_old_token_rejected_after_refresh(self, client):
        signup = self._signup(client)
        client.post(REFRESH_URL, json={"refresh_token": signup["refresh_token"]})
        resp = client.post(REFRESH_URL, json={"refresh_token": signup["refresh_token"]})
        assert resp.status_code == 401

    def test_unknown_token_returns_401(self, client):
        resp = client.post(REFRESH_URL, json={"refresh_token": "bogus-token"})
        assert resp.status_code == 401


class TestLogoutEndpoint:
    def _signup(self, client):
        return client.post(SIGNUP_URL, json=_signup_payload()).json()

    def test_logout_revokes_token(self, client):
        signup = self._signup(client)
        resp = client.post(LOGOUT_URL, json={"refresh_token": signup["refresh_token"]})
        assert resp.status_code == 204

        # The revoked token can no longer be used to refresh.
        resp = client.post(REFRESH_URL, json={"refresh_token": signup["refresh_token"]})
        assert resp.status_code == 401

    def test_logout_is_idempotent(self, client):
        signup = self._signup(client)
        assert client.post(LOGOUT_URL, json={"refresh_token": signup["refresh_token"]}).status_code == 204
        assert client.post(LOGOUT_URL, json={"refresh_token": signup["refresh_token"]}).status_code == 204


class TestMeEndpoint:
    def _auth_header(self, token):
        return {"Authorization": f"Bearer {token}"}

    def test_me_requires_access_token(self, client):
        assert client.get(ME_URL).status_code == 401
        assert client.get(ME_URL, headers=self._auth_header("garbage")).status_code == 401

    def test_me_returns_current_user(self, client):
        signup = client.post(SIGNUP_URL, json=_signup_payload()).json()
        resp = client.get(
            ME_URL, headers=self._auth_header(signup["access_token"])
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == "user@example.com"
        assert body["id"] == signup["user"]["id"]

    def test_me_rejects_deactivated_user(self, client, run_async):
        signup = client.post(SIGNUP_URL, json=_signup_payload()).json()

        async def deactivate(db):
            user = await db.execute(select(User).where(User.email == "user@example.com"))
            user.scalar_one().is_active = False
            await db.commit()

        run_async(deactivate)
        resp = client.get(ME_URL, headers=self._auth_header(signup["access_token"]))
        assert resp.status_code == 401
