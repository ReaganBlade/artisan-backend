"""Tests for SQLAlchemy model table configuration."""

import uuid

import pytest
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSONB

from media_service.db.base import SCHEMA
from sqlalchemy import Float

from media_service.models import Artwork, MediaFile, Profile


class TestProfileModel:
    def test_table_in_correct_schema(self):
        assert Profile.__table_args__["schema"] == SCHEMA

    def test_has_uuid_primary_key(self):
        pk_cols = [c for c in Profile.__table__.columns if c.primary_key]
        assert len(pk_cols) == 1

    def test_user_id_has_no_foreign_key(self):
        user_id_col = Profile.__table__.c.user_id
        assert len(list(user_id_col.foreign_keys)) == 0

    def test_user_id_is_unique(self):
        user_id_col = Profile.__table__.c.user_id
        assert user_id_col.unique is True

    def test_username_is_unique(self):
        username_col = Profile.__table__.c.username
        assert username_col.unique is True

    def test_social_links_is_jsonb(self):
        social_col = Profile.__table__.c.social_links
        assert isinstance(social_col.type, JSONB)

    def test_has_artworks_relationship(self):
        mapper = inspect(Profile)
        rel_names = [r.key for r in mapper.relationships]
        assert "artworks" in rel_names


class TestArtworkModel:
    def test_table_in_correct_schema(self):
        # __table_args__ is a tuple: (constraints..., {"schema": ...})
        table_args = Artwork.__table_args__
        assert table_args[-1]["schema"] == SCHEMA

    def test_has_uuid_primary_key(self):
        pk_cols = [c for c in Artwork.__table__.columns if c.primary_key]
        assert len(pk_cols) == 1

    def test_profile_id_has_foreign_key(self):
        fk_cols = [c for c in Artwork.__table__.columns if c.foreign_keys]
        fk_names = {c.name for c in fk_cols}
        assert "profile_id" in fk_names

    def test_price_uses_numeric(self):
        price_col = Artwork.__table__.c.price
        assert price_col.type.precision == 10
        assert price_col.type.scale == 2

    def test_price_is_not_float(self):
        price_col = Artwork.__table__.c.price
        assert not isinstance(price_col.type, Float)

    def test_art_type_is_indexed(self):
        art_type_col = Artwork.__table__.c.art_type
        assert art_type_col.index is True

    def test_status_is_indexed(self):
        status_col = Artwork.__table__.c.status
        assert status_col.index is True

    def test_has_profile_relationship(self):
        mapper = inspect(Artwork)
        rel_names = [r.key for r in mapper.relationships]
        assert "profile" in rel_names

    def test_has_media_files_relationship(self):
        mapper = inspect(Artwork)
        rel_names = [r.key for r in mapper.relationships]
        assert "media_files" in rel_names


class TestMediaFileModel:
    def test_table_in_correct_schema(self):
        assert MediaFile.__table_args__["schema"] == SCHEMA

    def test_has_uuid_primary_key(self):
        pk_cols = [c for c in MediaFile.__table__.columns if c.primary_key]
        assert len(pk_cols) == 1

    def test_artwork_id_has_foreign_key(self):
        fk_cols = [c for c in MediaFile.__table__.columns if c.foreign_keys]
        fk_names = {c.name for c in fk_cols}
        assert "artwork_id" in fk_names

    def test_artwork_id_is_indexed(self):
        artwork_id_col = MediaFile.__table__.c.artwork_id
        assert artwork_id_col.index is True

    def test_has_artwork_relationship(self):
        mapper = inspect(MediaFile)
        rel_names = [r.key for r in mapper.relationships]
        assert "artwork" in rel_names
