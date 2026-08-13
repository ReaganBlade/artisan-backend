import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import SCHEMA, Base


class AdminReviewFlag(Base):
    """Incident tracking for human admin review."""

    __tablename__ = "admin_review_flags"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # External ref to media_schema.artworks.id — no cross-schema FK by design.
    artwork_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    flag_reason: Mapped[str] = mapped_column(String(50), nullable=False)
    severity_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    # External ref to auth_schema.users.id — no cross-schema FK by design.
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
