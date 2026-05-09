from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.schemas.interests import InterestResponse, InterestedDeliveryGuyResponse
from app.models.interest import Interest
from app.models.listing import Listing


class InterestService:

    async def express_interest(
        self, listing_id: int, delivery_guy_id: int, db: AsyncSession
    ) -> InterestResponse:
        try:
            existing_interest = await db.execute(
                select(Interest).where(
                    Interest.listing_id == listing_id,
                    Interest.delivery_guy_id == delivery_guy_id,
                )
            )
            existing_interest = existing_interest.scalar_one_or_none()

            if existing_interest:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You have already expressed interest in this job.",
                )

            listing = await db.execute(
                select(Listing).where(
                    Listing.id == listing_id, Listing.status == "open"
                )
            )
            listing = listing.scalar_one_or_none()

            if not listing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This job listing is not open anymore.",
                )

            if listing.sender_id == delivery_guy_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You cannot express interest in your own job listing.",
                )

            new_interest = Interest(
                listing_id=listing_id,
                delivery_guy_id=delivery_guy_id,
            )
            db.add(new_interest)
            await db.commit()
            await db.refresh(new_interest)

            return InterestResponse(
                id=new_interest.id,
                listing_id=new_interest.listing_id,
                delivery_guy_id=new_interest.delivery_guy_id,
                status=new_interest.status.value,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    async def get_interests(
        self, sender_id: int, listing_id: int, db: AsyncSession
    ) -> list[InterestedDeliveryGuyResponse]:
        try:
            result = await db.execute(
                select(Listing)
                .options(selectinload(Listing.interests).selectinload(Interest.delivery_guy))
                .where(Listing.id == listing_id, Listing.sender_id == sender_id)
            )
            listing = result.scalar_one_or_none()

            if not listing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Listing not found or you are not the sender.",
                )
            if len(listing.interests) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No delivery guys have expressed interest in this listing yet.",
                )
                
            return [
                InterestedDeliveryGuyResponse(
                    id=interest.delivery_guy.id,
                    full_name=interest.delivery_guy.full_name,
                    email=interest.delivery_guy.email,
                    phone=interest.delivery_guy.phone,
                )
                for interest in listing.interests
                if interest.status == "interested"
            ]

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )
