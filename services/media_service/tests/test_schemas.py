"""Tests for Pydantic V2 schemas."""

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from media_service.schemas.artwork_schemas import (
    ArtworkCreate,
    ArtworkResponse,
    ArtworkUpdate,
)
from media_service.schemas.media_schemas import (
    MediaFileCreate,
    MediaFileResponse,
    MediaFileUpdate,
)
from media_service.schemas.profile_schemas import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
)
from media_service.models import Artwork, Profile


# ---------------------------------------------------------------------------
# Profile schemas
# ---------------------------------------------------------------------------

class TestProfileCreate:
    def test_valid(self):
        p = ProfileCreate(
            user_id=uuid.uuid4(),
            username="june",
            display_name="June Park",
        )
        assert p.username == "june"

    def test_missing_username_raises(self):
        with pytest.raises(ValidationError):
            ProfileCreate(user_id=uuid.uuid4(), display_name="June Park")

    def test_missing_display_name_raises(self):
        with pytest.raises(ValidationError):
            ProfileCreate(user_id=uuid.uuid4(), username="june")

    def test_username_max_length(self):
        with pytest.raises(ValidationError):
            ProfileCreate(
                user_id=uuid.uuid4(),
                username="x" * 51,
                display_name="Test",
            )

    def test_optional_fields_accept_none(self):
        p = ProfileCreate(
            user_id=uuid.uuid4(),
            username="june",
            display_name="June Park",
            bio=None,
            avatar_url=None,
            social_links=None,
        )
        assert p.bio is None


class TestProfileUpdate:
    def test_all_optional(self):
        u = ProfileUpdate()
        assert u.model_dump(exclude_unset=True) == {}

    def test_partial_update(self):
        u = ProfileUpdate(display_name="New Name")
        assert u.display_name == "New Name"


class TestProfileResponse:
    def test_from_attributes(self):
        config = ProfileResponse.model_config
        assert config.get("from_attributes") is True

    def test_from_model_instance(self):
        profile = Profile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            username="june",
            display_name="June Park",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        resp = ProfileResponse.model_validate(profile)
        assert resp.username == "june"


# ---------------------------------------------------------------------------
# Artwork schemas
# ---------------------------------------------------------------------------

class TestArtworkCreate:
    def test_valid(self):
        a = ArtworkCreate(
            profile_id=uuid.uuid4(),
            title="Sunshower",
            art_type="Print",
        )
        assert a.title == "Sunshower"

    def test_missing_title_raises(self):
        with pytest.raises(ValidationError):
            ArtworkCreate(profile_id=uuid.uuid4(), art_type="Print")

    def test_negative_price_raises(self):
        with pytest.raises(ValidationError):
            ArtworkCreate(
                profile_id=uuid.uuid4(),
                title="Test",
                art_type="Print",
                price=-1,
            )


class TestArtworkUpdate:
    def test_all_optional(self):
        u = ArtworkUpdate()
        assert u.model_dump(exclude_unset=True) == {}


class TestArtworkResponse:
    def test_from_attributes(self):
        config = ArtworkResponse.model_config
        assert config.get("from_attributes") is True

    def test_from_model_instance(self):
        artwork = Artwork(
            id=uuid.uuid4(),
            profile_id=uuid.uuid4(),
            title="Sunshower",
            art_type="Print",
            status="DRAFT",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        resp = ArtworkResponse.model_validate(artwork)
        assert resp.title == "Sunshower"


# ---------------------------------------------------------------------------
# MediaFile schemas
# ---------------------------------------------------------------------------

class TestMediaFileCreate:
    def test_valid(self):
        m = MediaFileCreate(
            artwork_id=uuid.uuid4(),
            file_url="https://storage.example.com/01.jpg",
            file_type="image/jpeg",
        )
        assert m.file_url.startswith("https://")


class TestMediaFileUpdate:
    def test_all_optional(self):
        u = MediaFileUpdate()
        assert u.model_dump(exclude_unset=True) == {}

    def test_partial_update(self):
        u = MediaFileUpdate(display_order=5)
        assert u.display_order == 5


class TestMediaFileResponse:
    def test_from_attributes(self):
        config = MediaFileResponse.model_config
        assert config.get("from_attributes") is True
