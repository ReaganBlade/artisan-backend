import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import SCHEMA, Base

if TYPE_CHECKING:
    from .profiles import Profile

    from .media_files import MediaFile


class Artwork(Base):
    """Master catalog record of an artwork."""

    __tablename__ = "artworks"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_artworks_price_non_negative"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    art_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    primary_media_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # -- relationships --
    profile: Mapped["Profile"] = relationship(back_populates="artworks")
    media_files: Mapped[list["MediaFile"]] = relationship(
        back_populates="artwork",
        cascade="all, delete-orphan",
    )
