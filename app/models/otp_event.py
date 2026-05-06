from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, Integer, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class OtpType(str, Enum):
    pickup = "pickup"
    delivery = "delivery"


class OtpEvent(Base):
    __tablename__ = "otp_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), nullable=False)
    otp_type: Mapped[OtpType] = mapped_column(
        SAEnum(
            OtpType,
            name="otp_type",
            native_enum=False,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    otp_hash: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fail_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
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
        back_populates="otp_events",
    )
