from datetime import datetime
from enum import Enum

from sqlalchemy import DECIMAL, Enum as SAEnum, ForeignKey, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ListingStatus(str, Enum):
    open = "open"
    pending = "pending"
    in_transit = "in_transit"
    delivered = "delivered"
    closed = "closed"


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    delivery_guy_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )
    origin_address: Mapped[str] = mapped_column(Text, nullable=False)
    origin_lat: Mapped[float] = mapped_column(DECIMAL(9, 6), nullable=False)
    origin_lng: Mapped[float] = mapped_column(DECIMAL(9, 6), nullable=False)
    dest_address: Mapped[str] = mapped_column(Text, nullable=False)
    dest_lat: Mapped[float] = mapped_column(DECIMAL(9, 6), nullable=False)
    dest_lng: Mapped[float] = mapped_column(DECIMAL(9, 6), nullable=False)
    distance_km: Mapped[float] = mapped_column(DECIMAL(8, 2), nullable=False)
    weight_kg: Mapped[float] = mapped_column(DECIMAL(5, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    offered_fare: Mapped[float] = mapped_column(DECIMAL(8, 2), nullable=False)
    status: Mapped[ListingStatus] = mapped_column(
        SAEnum(
            ListingStatus,
            name="listing_status",
            native_enum=False,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=ListingStatus.open,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    sender: Mapped["User"] = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_listings",
    )
    receiver: Mapped["User"] = relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_listings",
    )
    delivery_guy: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[delivery_guy_id],
        back_populates="delivered_listings",
    )
    images: Mapped[list["ListingImage"]] = relationship(
        "ListingImage",
        back_populates="listing",
        cascade="all, delete-orphan",
    )
    interests: Mapped[list["Interest"]] = relationship(
        "Interest",
        back_populates="listing",
        cascade="all, delete-orphan",
    )
    otp_events: Mapped[list["OtpEvent"]] = relationship(
        "OtpEvent",
        back_populates="listing",
        cascade="all, delete-orphan",
    )
