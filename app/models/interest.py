from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, Integer, TIMESTAMP, UniqueConstraint, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class InterestStatus(str, Enum):
    interested = "interested"
    selected = "selected"
    withdrawn = "withdrawn"


class Interest(Base):
    __tablename__ = "interests"

    __table_args__ = (
        UniqueConstraint("listing_id", "delivery_guy_id", name="uq_interest_listing_user"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), nullable=False)
    delivery_guy_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[InterestStatus] = mapped_column(
        SAEnum(
            InterestStatus,
            name="interest_status",
            native_enum=False,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=InterestStatus.interested,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    listing: Mapped["Listing"] = relationship(
        "Listing",
        back_populates="interests",
    )
    delivery_guy: Mapped["User"] = relationship(
        "User",
        foreign_keys=[delivery_guy_id],
        back_populates="interests",
    )
