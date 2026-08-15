"""initial moderation_schema (moderation_tasks, artwork_signatures, admin_review_flags)

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

SCHEMA = "moderation_schema"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    op.create_table(
        "moderation_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        # External ref to media_schema.artworks.id — no cross-schema FK by design.
        sa.Column("artwork_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "result_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
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
        "ix_moderation_tasks_artwork_id",
        "moderation_tasks",
        ["artwork_id"],
        schema=SCHEMA,
    )

    op.create_table(
        "artwork_signatures",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        # External ref to media_schema.artworks.id — no cross-schema FK by design.
        sa.Column("artwork_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phash", sa.String(64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_artwork_signatures_artwork_id",
        "artwork_signatures",
        ["artwork_id"],
        unique=True,
        schema=SCHEMA,
    )

    op.create_table(
        "admin_review_flags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        # External ref to media_schema.artworks.id — no cross-schema FK by design.
        sa.Column("artwork_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("flag_reason", sa.String(50), nullable=False),
        sa.Column("severity_score", sa.Numeric(5, 4), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        # External ref to auth_schema.users.id — no cross-schema FK by design.
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), nullable=True),
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
        "ix_admin_review_flags_artwork_id",
        "admin_review_flags",
        ["artwork_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_admin_review_flags_reviewed_by",
        "admin_review_flags",
        ["reviewed_by"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_admin_review_flags_reviewed_by",
        table_name="admin_review_flags",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_admin_review_flags_artwork_id",
        table_name="admin_review_flags",
        schema=SCHEMA,
    )
    op.drop_table("admin_review_flags", schema=SCHEMA)
    op.drop_index(
        "ix_artwork_signatures_artwork_id",
        table_name="artwork_signatures",
        schema=SCHEMA,
    )
    op.drop_table("artwork_signatures", schema=SCHEMA)
    op.drop_index(
        "ix_moderation_tasks_artwork_id",
        table_name="moderation_tasks",
        schema=SCHEMA,
    )
    op.drop_table("moderation_tasks", schema=SCHEMA)
    op.execute(f"DROP SCHEMA {SCHEMA}")
