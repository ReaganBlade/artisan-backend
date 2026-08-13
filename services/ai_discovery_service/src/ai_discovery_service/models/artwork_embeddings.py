import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import SCHEMA, Base


class ArtworkEmbedding(Base):
    """Vector embedding powering 'Vibe'/mood-based semantic search.

    Requires the `pgvector` extension on the target database
    (CREATE EXTENSION IF NOT EXISTS vector;) before table creation.
    """

    __tablename__ = "artwork_embeddings"
    __table_args__ = (
        Index("ix_artwork_embeddings_status_art_type", "status", "art_type"),
        Index(
            "ix_artwork_embeddings_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # External ref to media_schema.artworks.id — no cross-schema FK by design.
    artwork_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    embedding: Mapped[Vector] = mapped_column(Vector(512), nullable=False)
    # Denormalized from the Media service for pre-filtering.
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    art_type: Mapped[str] = mapped_column(String(50), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
