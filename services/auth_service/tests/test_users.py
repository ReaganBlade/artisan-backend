"""Tests for user-profile API endpoints."""

import pytest

pytestmark = pytest.mark.usefixtures("_clean_tables_between_tests")

SIGNUP_URL = "/api/v1/auth/signup"
ME_URL = "/api/v1/users/me"
USERS_URL = "/api/v1/users"


def _signup_payload(email="user@example.com", password="password123"):
    return {"email": email, "password": password}


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


class TestMeEndpoint:
    def test_me_returns_current_user(self, client):
        signup = client.post(SIGNUP_URL, json=_signup_payload()).json()
        resp = client.get(ME_URL, headers=_auth_header(signup["access_token"]))
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == "user@example.com"
        assert body["id"] == signup["user"]["id"]
        assert "hashed_password" not in body

    def test_me_requires_authentication(self, client):
        assert client.get(ME_URL).status_code == 401

    def test_me_rejects_invalid_token(self, client):
        assert client.get(ME_URL, headers=_auth_header("garbage")).status_code == 401


class TestGetUserEndpoint:
    def test_get_user_by_id(self, client):
        signup = client.post(SIGNUP_URL, json=_signup_payload()).json()
        user_id = signup["user"]["id"]
        resp = client.get(
            f"{USERS_URL}/{user_id}", headers=_auth_header(signup["access_token"])
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == user_id
        assert resp.json()["email"] == "user@example.com"

    def test_get_user_not_found(self, client):
        signup = client.post(SIGNUP_URL, json=_signup_payload()).json()
        resp = client.get(
            f"{USERS_URL}/00000000-0000-0000-0000-000000000000",
            headers=_auth_header(signup["access_token"]),
        )
        assert resp.status_code == 404

    def test_get_user_requires_auth(self, client):
        resp = client.get(
            f"{USERS_URL}/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 401


class TestPatchUserEndpoint:
    def test_update_own_profile(self, client):
        signup = client.post(SIGNUP_URL, json=_signup_payload()).json()
        user_id = signup["user"]["id"]
        resp = client.patch(
            f"{USERS_URL}/{user_id}",
            json={"email": "newemail@example.com"},
            headers=_auth_header(signup["access_token"]),
        )
        assert resp.status_code == 200
        assert resp.json()["email"] == "newemail@example.com"

    def test_cannot_update_other_user(self, client):
        signup1 = client.post(
            SIGNUP_URL, json=_signup_payload(email="a@example.com")
        ).json()
        signup2 = client.post(
            SIGNUP_URL, json=_signup_payload(email="b@example.com")
        ).json()
        other_id = signup2["user"]["id"]
        resp = client.patch(
            f"{USERS_URL}/{other_id}",
            json={"email": "hacked@example.com"},
            headers=_auth_header(signup1["access_token"]),
        )
        assert resp.status_code == 403

    def test_update_rejects_duplicate_email(self, client):
        client.post(SIGNUP_URL, json=_signup_payload(email="taken@example.com"))
        signup = client.post(
            SIGNUP_URL, json=_signup_payload(email="mine@example.com")
        ).json()
        user_id = signup["user"]["id"]
        resp = client.patch(
            f"{USERS_URL}/{user_id}",
            json={"email": "taken@example.com"},
            headers=_auth_header(signup["access_token"]),
        )
        assert resp.status_code == 409

    def test_update_requires_auth(self, client):
        resp = client.patch(
            f"{USERS_URL}/00000000-0000-0000-0000-000000000000",
            json={"email": "x@example.com"},
        )
        assert resp.status_code == 401
