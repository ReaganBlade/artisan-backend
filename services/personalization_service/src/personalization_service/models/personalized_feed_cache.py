import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import SCHEMA, Base


class PersonalizedFeedCache(Base):
    """Just-In-Time pre-calculated ordered list of artworks for a user's feed (1:1)."""

    __tablename__ = "personalized_feed_cache"
    __table_args__ = {"schema": SCHEMA}

    # External ref to auth_schema.users.id — no cross-schema FK by design.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    cached_artwork_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), nullable=False, default=list, server_default="{}"
    )
    last_calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
