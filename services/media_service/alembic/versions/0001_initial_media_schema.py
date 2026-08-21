"""initial media_schema (profiles, artworks, media_files)

Revision ID: 0001
Revises:
Create Date: 2026-08-14 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "media_schema"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    op.create_table(
        "profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        # External ref to auth_schema.users.id — no cross-schema FK by design.
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.String(512), nullable=True),
        sa.Column("cover_image_url", sa.String(512), nullable=True),
        sa.Column(
            "social_links",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_profiles_user_id", "profiles", ["user_id"], unique=True, schema=SCHEMA
    )
    op.create_index(
        "ix_profiles_username",
        "profiles",
        ["username"],
        unique=True,
        schema=SCHEMA,
    )

    op.create_table(
        "artworks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("art_type", sa.String(50), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("primary_media_url", sa.String(512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "price >= 0", name="ck_artworks_price_non_negative"
        ),
        sa.ForeignKeyConstraint(
            ["profile_id"],
            [f"{SCHEMA}.profiles.id"],
            ondelete="CASCADE",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_artworks_profile_id",
        "artworks",
        ["profile_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_artworks_status", "artworks", ["status"], schema=SCHEMA
    )
    op.create_index(
        "ix_artworks_art_type", "artworks", ["art_type"], schema=SCHEMA
    )

    op.create_table(
        "media_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("artwork_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_url", sa.String(512), nullable=False),
        sa.Column("file_type", sa.String(50), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column(
            "display_order",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["artwork_id"],
            [f"{SCHEMA}.artworks.id"],
            ondelete="CASCADE",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_media_files_artwork_id",
        "media_files",
        ["artwork_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_media_files_artwork_id", table_name="media_files", schema=SCHEMA
    )
    op.drop_table("media_files", schema=SCHEMA)
    op.drop_index("ix_artworks_art_type", table_name="artworks", schema=SCHEMA)
    op.drop_index("ix_artworks_status", table_name="artworks", schema=SCHEMA)
    op.drop_index(
        "ix_artworks_profile_id", table_name="artworks", schema=SCHEMA
    )
    op.drop_table("artworks", schema=SCHEMA)
    op.drop_index("ix_profiles_username", table_name="profiles", schema=SCHEMA)
    op.drop_index("ix_profiles_user_id", table_name="profiles", schema=SCHEMA)
    op.drop_table("profiles", schema=SCHEMA)
    op.execute(f"DROP SCHEMA {SCHEMA}")
