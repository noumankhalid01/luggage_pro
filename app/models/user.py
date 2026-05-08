from datetime import datetime
from enum import Enum

from sqlalchemy import String, Text, TIMESTAMP, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    cnic_image_url: Mapped[str] = mapped_column(Text, nullable=False)
    fcm_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(
            UserStatus,
            name="user_status",
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=UserStatus.ACTIVE,
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

    sent_listings: Mapped[list["Listing"]] = relationship(
        "Listing",
        foreign_keys="Listing.sender_id",
        back_populates="sender",
    )
    delivered_listings: Mapped[list["Listing"]] = relationship(
        "Listing",
        foreign_keys="Listing.delivery_guy_id",
        back_populates="delivery_guy",
    )
    interests: Mapped[list["Interest"]] = relationship(
        "Interest",
        foreign_keys="Interest.delivery_guy_id",
        back_populates="delivery_guy",
    )
