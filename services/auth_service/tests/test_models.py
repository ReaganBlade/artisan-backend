"""Tests for SQLAlchemy model definitions, metadata, and schema qualification."""

import importlib

from auth_service.db.base import SCHEMA, Base
from auth_service.models import RefreshToken, User, UserRole
from auth_service.models.user_role import UserRole as UserRoleDirect


class TestUserRoleEnum:
    def test_has_required_values(self):
        assert UserRole.CUSTOMER == "CUSTOMER"
        assert UserRole.ARTIST == "ARTIST"
        assert UserRole.ADMIN == "ADMIN"

    def test_is_string_enum(self):
        assert isinstance(UserRole.CUSTOMER, str)
        assert isinstance(UserRole("ARTIST"), UserRole)

    def test_direct_import_matches(self):
        assert UserRoleDirect is UserRole


class TestUserModel:
    def test_tablename(self):
        assert User.__tablename__ == "users"

    def test_schema_qualification(self):
        assert User.__table_args__["schema"] == SCHEMA

    def test_schema_is_auth_schema(self):
        assert SCHEMA == "auth_schema"


class TestRefreshTokenModel:
    def test_tablename(self):
        assert RefreshToken.__tablename__ == "refresh_tokens"

    def test_schema_qualification(self):
        assert RefreshToken.__table_args__["schema"] == SCHEMA

    def test_schema_is_auth_schema(self):
        assert SCHEMA == "auth_schema"


class TestMetadata:
    def test_all_tables_in_auth_schema(self):
        """Every table registered on Base.metadata must belong to auth_schema."""
        for table_name, table in Base.metadata.tables.items():
            assert table.schema == SCHEMA, (
                f"Table {table_name!r} has schema {table.schema!r}, expected {SCHEMA!r}"
            )

    def test_users_table_exists(self):
        assert f"{SCHEMA}.users" in Base.metadata.tables

    def test_refresh_tokens_table_exists(self):
        assert f"{SCHEMA}.refresh_tokens" in Base.metadata.tables

    def test_refresh_tokens_fk_references_users(self):
        """The refresh_tokens.user_id FK must reference auth_schema.users.id."""
        rt_table = Base.metadata.tables[f"{SCHEMA}.refresh_tokens"]
        fk_names = [fk.name for fk in rt_table.foreign_keys]
        assert any("users.id" in str(fk) for fk in rt_table.foreign_keys)


class TestCircularImportPrevention:
    """Verify that importing models individually and together does not fail."""

    def test_import_user(self):
        mod = importlib.import_module("auth_service.models.user")
        assert hasattr(mod, "User")

    def test_import_refresh_token(self):
        mod = importlib.import_module("auth_service.models.refresh_token")
        assert hasattr(mod, "RefreshToken")

    def test_import_user_role(self):
        mod = importlib.import_module("auth_service.models.user_role")
        assert hasattr(mod, "UserRole")

    def test_import_all_models_together(self):
        from auth_service.models import RefreshToken, User, UserRole  # noqa: F401

    def test_app_startup_imports(self):
        """Importing main should not raise (no circular dependency at startup)."""
        importlib.import_module("auth_service.main")
