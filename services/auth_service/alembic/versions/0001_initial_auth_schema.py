"""initial auth_schema (users, refresh_tokens)

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

SCHEMA = "auth_schema"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    # Matches models/user_role.py: UserRole.CUSTOMER / ARTIST / ADMIN.
    # create_type=False: the type is created explicitly by SQLAlchemy when the
    # table is created, so it is only emitted once.
    user_role = postgresql.ENUM(
        "CUSTOMER",
        "ARTIST",
        "ADMIN",
        name="user_role",
        schema=SCHEMA,
        create_type=False,
    )
    op.execute(
        f"CREATE TYPE {SCHEMA}.user_role AS ENUM ('CUSTOMER', 'ARTIST', 'ADMIN')"
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column(
            "role",
            user_role,
            nullable=False,
            server_default="CUSTOMER",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
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
        "ix_users_email", "users", ["email"], unique=True, schema=SCHEMA
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.String(512), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "is_revoked",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            [f"{SCHEMA}.users.id"],
            ondelete="CASCADE",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_refresh_tokens_user_id",
        "refresh_tokens",
        ["user_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_refresh_tokens_token",
        "refresh_tokens",
        ["token"],
        unique=True,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_refresh_tokens_token", table_name="refresh_tokens", schema=SCHEMA
    )
    op.drop_index(
        "ix_refresh_tokens_user_id", table_name="refresh_tokens", schema=SCHEMA
    )
    op.drop_table("refresh_tokens", schema=SCHEMA)
    op.drop_index("ix_users_email", table_name="users", schema=SCHEMA)
    op.drop_table("users", schema=SCHEMA)
    op.execute(f"DROP TYPE {SCHEMA}.user_role")
    op.execute(f"DROP SCHEMA {SCHEMA}")
