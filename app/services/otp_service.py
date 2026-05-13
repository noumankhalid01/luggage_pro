import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.models.listing import Listing, ListingStatus
from app.models.otp_event import OtpEvent, OtpType
from app.models.user import User
from app.schemas.notifications import Notification
from app.schemas.otp_events import SendOtpRequest, SendOtpResponse, VerifyOtpRequest, VerifyOtpResponse
from app.utils.notifications import send_push_notification


class OtpService:
    async def send_pickup_otp(
        self,
        payload: SendOtpRequest,
        current_user: User,
        db: AsyncSession,
    ) -> SendOtpResponse:
        try:
            listing = await db.get(Listing, payload.listing_id)
            if not listing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Listing not found",
                )

            if listing.sender_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to send OTP for this listing.",
                )

            if listing.status != ListingStatus.pending:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="OTP can only be sent for a pending listing.",
                )

            if not listing.delivery_guy_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No delivery guy has been selected for this listing.",
                )

            delivery_guy = await db.get(User, listing.delivery_guy_id)
            if not delivery_guy or not delivery_guy.fcm_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Selected delivery guy does not have a valid push token. Ask him to log in to the app to refresh his token.",
                )

            otp_event_stmt = (
                select(OtpEvent)
                .where(
                    OtpEvent.listing_id == listing.id,
                    OtpEvent.otp_type == payload.otp_type,
                    OtpEvent.used == False
                )
                .order_by(OtpEvent.id.desc())
            )
            otp_event = await db.scalar(otp_event_stmt)

            if payload.resend:
                if not otp_event:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="No existing OTP found to resend.",
                    )
            elif otp_event:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An active OTP already exists for this listing.",
                )

            otp_code = f"{secrets.randbelow(900000) + 100000}"
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

            if otp_event and payload.resend:
                otp_event.otp_hash = otp_code
                otp_event.expires_at = expires_at
            else:
                otp_event = OtpEvent(
                    listing_id=listing.id,
                    otp_type=payload.otp_type,
                    otp_hash=otp_code,
                    expires_at=expires_at,
                    used=False,
                    fail_count=0,
                )
                db.add(otp_event)

            await db.flush()
            await db.commit()
            await db.refresh(otp_event)

            notification = Notification(
                fcm_token=delivery_guy.fcm_token,
                title="LuggagePro OTP",
                body=f"Your {payload.otp_type.value} OTP is {otp_code}. It expires in 5 minutes.",
                data={
                    "listing_id": str(listing.id),
                    "otp_type": payload.otp_type.value,
                    "otp_code": otp_code,
                },
            )

            sent = await run_in_threadpool(send_push_notification, notification)
            if not sent:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="OTP was saved, but push notification could not be delivered.",
                )

            return SendOtpResponse(
                message=(
                    "OTP resent successfully to the delivery guy."
                    if payload.resend
                    else "OTP sent successfully to the delivery guy."
                ),
                otp_event_id=otp_event.id,
                listing_id=listing.id,
                otp_type=payload.otp_type,
                expires_at=otp_event.expires_at,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    async def verify_otp(
        self,
        payload: VerifyOtpRequest,
        current_user: User,
        db: AsyncSession,
    ) -> VerifyOtpResponse:
        try:
            now = datetime.now(timezone.utc)
            listing = None

            if payload.otp_type != OtpType.reset_password:
                if payload.listing_id is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="listing_id is required for listing OTP verification.",
                    )

                listing = await db.get(Listing, payload.listing_id)
                if not listing:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Listing not found",
                    )

            if payload.otp_type == OtpType.pickup:
                if listing.sender_id != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You are not authorized to verify this OTP.",
                    )
                if listing.status != ListingStatus.pending:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Pickup OTP can only be verified for a pending listing.",
                    )

            elif payload.otp_type == OtpType.delivery:
                if listing.delivery_guy_id != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You are not authorized to verify this OTP.",
                    )
                if listing.status != ListingStatus.in_transit:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Delivery OTP can only be verified for an in-transit listing.",
                    )

            otp_event_stmt = select(OtpEvent).where(
                OtpEvent.otp_type == payload.otp_type,
                OtpEvent.otp_hash == payload.otp_code,
                OtpEvent.used == False,
                OtpEvent.expires_at > now,
            )
            if payload.listing_id is not None:
                otp_event_stmt = otp_event_stmt.where(OtpEvent.listing_id == payload.listing_id)

            otp_event = await db.scalar(otp_event_stmt.order_by(OtpEvent.id.desc()))
            if not otp_event:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired OTP.",
                )

            otp_event.used = True

            listing_status = None
            if payload.otp_type == OtpType.pickup:
                listing.status = ListingStatus.in_transit
                listing_status = listing.status.value
            elif payload.otp_type == OtpType.delivery:
                listing.status = ListingStatus.delivered
                listing_status = listing.status.value
            elif payload.otp_type == OtpType.reset_password:
                listing_status = None

            await db.commit()
            await db.refresh(otp_event)

            return VerifyOtpResponse(
                message="OTP verified successfully.",
                otp_event_id=otp_event.id,
                otp_type=payload.otp_type,
                listing_id=otp_event.listing_id if payload.otp_type != OtpType.reset_password else None,
                listing_status=listing_status,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
