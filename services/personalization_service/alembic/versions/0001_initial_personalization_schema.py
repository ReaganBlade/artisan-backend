"""initial personalization_schema (user_interactions, personalized_feed_cache)

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

SCHEMA = "personalization_schema"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    op.create_table(
        "user_interactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        # External ref to auth_schema.users.id — no cross-schema FK by design.
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        # External ref to media_schema.artworks.id — no cross-schema FK by design.
        sa.Column("artwork_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("interaction_type", sa.String(20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "user_id",
            "artwork_id",
            "interaction_type",
            name="uq_user_interactions_user_artwork_type",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_user_interactions_user_id",
        "user_interactions",
        ["user_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_user_interactions_artwork_id",
        "user_interactions",
        ["artwork_id"],
        schema=SCHEMA,
    )

    op.create_table(
        "personalized_feed_cache",
        # External ref to auth_schema.users.id — no cross-schema FK by design.
        # The user_id doubles as the primary key (1:1 relation per user).
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "cached_artwork_ids",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=False,
            server_default=sa.text("'{}'::uuid[]"),
        ),
        sa.Column(
            "last_calculated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("personalized_feed_cache", schema=SCHEMA)
    op.drop_index(
        "ix_user_interactions_artwork_id",
        table_name="user_interactions",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_user_interactions_user_id",
        table_name="user_interactions",
        schema=SCHEMA,
    )
    op.drop_table("user_interactions", schema=SCHEMA)
    op.execute(f"DROP SCHEMA {SCHEMA}")
