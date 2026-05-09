from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.interests import InterestResponse
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
                select(Listing).where(Listing.id == listing_id, Listing.status == "open")
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
