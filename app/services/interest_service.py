from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.schemas.interests import InterestResponse, InterestedDeliveryGuyResponse, SelectInterestResponse, WithdrawInterestResponse
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
                    interest_id=interest.id,
                    delivery_guy_id=interest.delivery_guy.id,
                    full_name=interest.delivery_guy.full_name,
                    email=interest.delivery_guy.email,
                    phone=interest.delivery_guy.phone,
                    status=interest.status.value,
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

    async def select_delivery_guy(self, interest_id: int, sender_id: int, db: AsyncSession) -> SelectInterestResponse:
        try:
            result = await db.execute(
                select(Interest)
                .options(selectinload(Interest.listing))
                .where(Interest.id == interest_id)
            )
            interest = result.scalar_one_or_none()

            if not interest:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Interest not found.",
                )
            if interest.listing.sender_id != sender_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to select a delivery guy for this listing.",
                )
            if interest.status != "interested":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This interest cannot be selected.",
                )

            if interest.listing.status != "open":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You have already selected a delivery guy for this listing.",
                )

            interest.status = "selected"
            interest.listing.status = "pending"
            interest.listing.delivery_guy_id = interest.delivery_guy_id

            await db.commit()
            await db.refresh(interest)

            return SelectInterestResponse(
                interest_id=interest.id,
                listing_id=interest.listing_id,
                delivery_guy_id=interest.delivery_guy_id,
                status=interest.status.value,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    async def withdraw_interest_traveller(self, interest_id: int, delivery_guy_id: int, db: AsyncSession) -> WithdrawInterestResponse:
        try:
            result = await db.execute(
                select(Interest)
                .options(selectinload(Interest.listing))
                .where(Interest.id == interest_id)
            )
            interest = result.scalar_one_or_none()

            if not interest:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Interest not found.",
                )
            if interest.delivery_guy_id != delivery_guy_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to withdraw this interest.",
                )

            if interest.status == "selected" and interest.listing.status != "pending":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You cannot withdraw this job.",
                )

            if interest.listing.delivery_guy_id == delivery_guy_id:
                interest.listing.status = "open"
                interest.listing.delivery_guy_id = None
            
            interest.status = "withdrawn"
            await db.commit()

            return WithdrawInterestResponse(success=True)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    async def withdraw_interest_sender(self, interest_id: int, sender_id: int, db: AsyncSession) -> WithdrawInterestResponse:
        try:
            result = await db.execute(
                select(Interest)
                .options(selectinload(Interest.listing))
                .where(Interest.id == interest_id)
            )
            interest = result.scalar_one_or_none()

            if not interest:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Interest not found.",
                )
            if interest.listing.sender_id != sender_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to withdraw this interest.",
                )
            if interest.status == "selected" and interest.listing.status != "pending":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You cannot withdraw this job.",
                )

            if interest.status == "selected" and interest.listing.status == "pending":
                interest.status = "withdrawn"
                interest.listing.delivery_guy_id = None
                interest.listing.status = "open"
            else:
                interest.status = "withdrawn"
            
            await db.commit()

            return WithdrawInterestResponse(success=True)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )
