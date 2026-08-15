"""initial ai_discovery_schema (artwork_embeddings, search_query_logs)

Revision ID: 0001
Revises:
Create Date: 2026-08-14 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "ai_discovery_schema"


def upgrade() -> None:
    # pgvector powers the semantic "Vibe" search (artwork_embeddings.embedding).
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    op.create_table(
        "artwork_embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        # External ref to media_schema.artworks.id — no cross-schema FK by design.
        sa.Column("artwork_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("embedding", Vector(512), nullable=False),
        # Denormalized from the Media service for pre-filtering.
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("art_type", sa.String(50), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_artwork_embeddings_artwork_id",
        "artwork_embeddings",
        ["artwork_id"],
        unique=True,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_artwork_embeddings_status_art_type",
        "artwork_embeddings",
        ["status", "art_type"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_artwork_embeddings_embedding_hnsw",
        "artwork_embeddings",
        ["embedding"],
        unique=False,
        schema=SCHEMA,
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )

    op.create_table(
        "search_query_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        # External ref to auth_schema.users.id — no cross-schema FK by design.
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("is_semantic", sa.Boolean(), nullable=False),
        sa.Column("result_count", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_search_query_logs_user_id",
        "search_query_logs",
        ["user_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_search_query_logs_user_id",
        table_name="search_query_logs",
        schema=SCHEMA,
    )
    op.drop_table("search_query_logs", schema=SCHEMA)
    op.drop_index(
        "ix_artwork_embeddings_embedding_hnsw",
        table_name="artwork_embeddings",
        schema=SCHEMA,
        postgresql_using="hnsw",
    )
    op.drop_index(
        "ix_artwork_embeddings_status_art_type",
        table_name="artwork_embeddings",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_artwork_embeddings_artwork_id",
        table_name="artwork_embeddings",
        schema=SCHEMA,
    )
    op.drop_table("artwork_embeddings", schema=SCHEMA)
    op.execute(f"DROP SCHEMA {SCHEMA}")
