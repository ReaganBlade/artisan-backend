import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import SCHEMA, Base


class UserInteraction(Base):
    """Append-only ledger of binary engagement metrics."""

    __tablename__ = "user_interactions"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "artwork_id",
            "interaction_type",
            name="uq_user_interactions_user_artwork_type",
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # External ref to auth_schema.users.id — no cross-schema FK by design.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    # External ref to media_schema.artworks.id — no cross-schema FK by design.
    artwork_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    interaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
