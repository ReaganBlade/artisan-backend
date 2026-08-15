"""initial commerce_schema (orders, order_items)

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

SCHEMA = "commerce_schema"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        # External ref to auth_schema.users.id — no cross-schema FK by design.
        sa.Column("buyer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_status", sa.String(20), nullable=False),
        sa.Column("fulfillment_status", sa.String(20), nullable=False),
        sa.Column("stripe_session_id", sa.String(255), nullable=True),
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
        "ix_orders_buyer_id", "orders", ["buyer_id"], schema=SCHEMA
    )
    op.create_index(
        "ix_orders_stripe_session_id",
        "orders",
        ["stripe_session_id"],
        unique=True,
        schema=SCHEMA,
    )

    op.create_table(
        "order_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        # External ref to media_schema.artworks.id — no cross-schema FK by design.
        sa.Column("artwork_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("price_at_purchase", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            [f"{SCHEMA}.orders.id"],
            ondelete="CASCADE",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_order_items_order_id",
        "order_items",
        ["order_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_order_items_artwork_id",
        "order_items",
        ["artwork_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_order_items_artwork_id", table_name="order_items", schema=SCHEMA
    )
    op.drop_index(
        "ix_order_items_order_id", table_name="order_items", schema=SCHEMA
    )
    op.drop_table("order_items", schema=SCHEMA)
    op.drop_index(
        "ix_orders_stripe_session_id", table_name="orders", schema=SCHEMA
    )
    op.drop_index("ix_orders_buyer_id", table_name="orders", schema=SCHEMA)
    op.drop_table("orders", schema=SCHEMA)
    op.execute(f"DROP SCHEMA {SCHEMA}")
