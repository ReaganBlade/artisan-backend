"""API endpoint tests for the media service.

These tests require a running PostgreSQL database.
"""

import pytest

pytestmark = pytest.mark.usefixtures("_clean_tables_between_tests")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

USER_ID = "33333333-3333-3333-3333-333333333301"


def _profile_payload(username="june", display_name="June Park", **overrides):
    data = {
        "user_id": USER_ID,
        "username": username,
        "display_name": display_name,
    }
    data.update(overrides)
    return data


def _artwork_payload(profile_id, **overrides):
    data = {
        "profile_id": str(profile_id),
        "title": "Sunshower",
        "art_type": "Print",
        "price": "240.00",
        "status": "DRAFT",
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------------------
# Profile CRUD
# ---------------------------------------------------------------------------

class TestProfileAPI:
    def test_create_profile_returns_201(self, client):
        resp = client.post("/api/v1/profiles", json=_profile_payload())
        assert resp.status_code == 201
        body = resp.json()
        assert body["username"] == "june"
        assert body["display_name"] == "June Park"
        assert "id" in body

    def test_get_profile_returns_200(self, client):
        created = client.post("/api/v1/profiles", json=_profile_payload()).json()
        resp = client.get(f"/api/v1/profiles/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["username"] == "june"

    def test_get_nonexistent_profile_returns_404(self, client):
        resp = client.get(
            "/api/v1/profiles/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 404

    def test_list_profiles_returns_200(self, client):
        client.post("/api/v1/profiles", json=_profile_payload())
        resp = client.get("/api/v1/profiles")
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert body["total"] >= 1

    def test_update_profile_returns_200(self, client):
        created = client.post("/api/v1/profiles", json=_profile_payload()).json()
        resp = client.patch(
            f"/api/v1/profiles/{created['id']}",
            json={"display_name": "New Name"},
        )
        assert resp.status_code == 200
        assert resp.json()["display_name"] == "New Name"

    def test_update_nonexistent_profile_returns_404(self, client):
        resp = client.patch(
            "/api/v1/profiles/00000000-0000-0000-0000-000000000000",
            json={"display_name": "X"},
        )
        assert resp.status_code == 404

    def test_delete_profile_returns_204(self, client):
        created = client.post("/api/v1/profiles", json=_profile_payload()).json()
        resp = client.delete(f"/api/v1/profiles/{created['id']}")
        assert resp.status_code == 204
        # Verify it's gone
        resp = client.get(f"/api/v1/profiles/{created['id']}")
        assert resp.status_code == 404

    def test_delete_nonexistent_profile_returns_404(self, client):
        resp = client.delete(
            "/api/v1/profiles/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 404

    def test_get_profile_by_username(self, client):
        client.post("/api/v1/profiles", json=_profile_payload())
        resp = client.get("/api/v1/profiles/by-username/june")
        assert resp.status_code == 200
        assert resp.json()["username"] == "june"

    def test_get_profile_by_username_not_found(self, client):
        resp = client.get("/api/v1/profiles/by-username/ghost")
        assert resp.status_code == 404

    def test_duplicate_username_returns_409(self, client):
        client.post("/api/v1/profiles", json=_profile_payload())
        resp = client.post("/api/v1/profiles", json=_profile_payload())
        assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Artwork CRUD
# ---------------------------------------------------------------------------

class TestArtworkAPI:
    def _create_profile(self, client):
        return client.post("/api/v1/profiles", json=_profile_payload()).json()

    def test_create_artwork_returns_201(self, client):
        profile = self._create_profile(client)
        resp = client.post("/api/v1/artworks", json=_artwork_payload(profile["id"]))
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "Sunshower"

    def test_get_artwork_returns_200(self, client):
        profile = self._create_profile(client)
        created = client.post(
            "/api/v1/artworks", json=_artwork_payload(profile["id"])
        ).json()
        resp = client.get(f"/api/v1/artworks/{created['id']}")
        assert resp.status_code == 200

    def test_get_nonexistent_artwork_returns_404(self, client):
        resp = client.get(
            "/api/v1/artworks/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 404

    def test_list_artworks_returns_200(self, client):
        profile = self._create_profile(client)
        client.post("/api/v1/artworks", json=_artwork_payload(profile["id"]))
        resp = client.get("/api/v1/artworks")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_list_artworks_filter_by_profile(self, client):
        profile = self._create_profile(client)
        client.post("/api/v1/artworks", json=_artwork_payload(profile["id"]))
        resp = client.get(f"/api/v1/artworks?profile_id={profile['id']}")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_update_artwork_returns_200(self, client):
        profile = self._create_profile(client)
        created = client.post(
            "/api/v1/artworks", json=_artwork_payload(profile["id"])
        ).json()
        resp = client.patch(
            f"/api/v1/artworks/{created['id']}",
            json={"title": "Updated Title"},
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated Title"

    def test_delete_artwork_returns_204(self, client):
        profile = self._create_profile(client)
        created = client.post(
            "/api/v1/artworks", json=_artwork_payload(profile["id"])
        ).json()
        resp = client.delete(f"/api/v1/artworks/{created['id']}")
        assert resp.status_code == 204

    def test_list_profile_artworks(self, client):
        profile = self._create_profile(client)
        client.post("/api/v1/artworks", json=_artwork_payload(profile["id"]))
        resp = client.get(f"/api/v1/profiles/{profile['id']}/artworks")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1


# ---------------------------------------------------------------------------
# Media file operations
# ---------------------------------------------------------------------------

class TestMediaAPI:
    def _setup(self, client):
        """Create a profile and artwork, return artwork dict."""
        profile = client.post(
            "/api/v1/profiles", json=_profile_payload()
        ).json()
        artwork = client.post(
            "/api/v1/artworks", json=_artwork_payload(profile["id"])
        ).json()
        return artwork

    def test_list_media_for_artwork(self, client):
        artwork = self._setup(client)
        resp = client.get(f"/api/v1/artworks/{artwork['id']}/media")
        assert resp.status_code == 200
        assert "items" in resp.json()

    def test_list_media_for_nonexistent_artwork_returns_404(self, client):
        resp = client.get(
            "/api/v1/artworks/00000000-0000-0000-0000-000000000000/media"
        )
        assert resp.status_code == 404

    def test_update_media_returns_200(self, client, run_async):
        """Test PATCH /media/{media_id} by creating a record directly."""
        from media_service.models import MediaFile
        from media_service.schemas.media_schemas import MediaFileCreate

        artwork = self._setup(client)

        # Insert a media file directly via DB
        async def _insert_media(db):
            media = MediaFile(
                artwork_id=artwork["id"],
                file_url="https://storage.example.com/01.jpg",
                file_type="image/jpeg",
                display_order=0,
            )
            db.add(media)
            await db.commit()
            await db.refresh(media)
            return str(media.id)

        media_id = run_async(_insert_media)

        resp = client.patch(
            f"/api/v1/media/{media_id}",
            json={"display_order": 3},
        )
        assert resp.status_code == 200
        assert resp.json()["display_order"] == 3

    def test_update_nonexistent_media_returns_404(self, client):
        resp = client.patch(
            "/api/v1/media/00000000-0000-0000-0000-000000000000",
            json={"display_order": 1},
        )
        assert resp.status_code == 404

    def test_delete_media_returns_204(self, client, run_async):
        """Test DELETE /media/{media_id}."""
        from media_service.models import MediaFile

        artwork = self._setup(client)

        async def _insert_media(db):
            media = MediaFile(
                artwork_id=artwork["id"],
                file_url="https://storage.example.com/01.jpg",
                file_type="image/jpeg",
                display_order=0,
            )
            db.add(media)
            await db.commit()
            await db.refresh(media)
            return str(media.id)

        media_id = run_async(_insert_media)

        resp = client.delete(f"/api/v1/media/{media_id}")
        assert resp.status_code == 204

        # Verify it's gone
        resp = client.get(f"/api/v1/media/{media_id}")
        assert resp.status_code in (404, 405)  # 405 if route doesn't exist for GET

    def test_delete_nonexistent_media_returns_404(self, client):
        resp = client.delete(
            "/api/v1/media/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 404
