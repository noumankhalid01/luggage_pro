from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import Listing
from app.models.listing_image import ListingImage
from app.models.user import User
from app.schemas.listings import (
    CreateListingRequest,
    CreateListingResponse,
    GetListingsResponse,
    CloseListingResponse,
)
from app.utils.maps import get_distance_km
from app.utils.calculate_fare import calculate_fare


class ListingService:
    async def create_listing(
        self,
        listing_data: CreateListingRequest,
        current_user: User,
        db: AsyncSession,
    ) -> CreateListingResponse:
        try:
            if not listing_data.image_urls:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one image is required.",
                )

            if len(listing_data.image_urls) > 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A listing can have at most 3 images.",
                )

            distance_km = get_distance_km(
                listing_data.origin_lat,
                listing_data.origin_lng,
                listing_data.dest_lat,
                listing_data.dest_lng,
            )
            offered_fare = calculate_fare(distance_km, listing_data.weight_kg)

            new_listing = Listing(
                sender_id=current_user.id,
                receiver_phone=listing_data.receiver_phone,
                origin_address=listing_data.origin_address,
                origin_lat=listing_data.origin_lat,
                origin_lng=listing_data.origin_lng,
                dest_address=listing_data.dest_address,
                dest_lat=listing_data.dest_lat,
                dest_lng=listing_data.dest_lng,
                distance_km=distance_km,
                weight_kg=listing_data.weight_kg,
                description=listing_data.description.lower(),
                offered_fare=offered_fare,
                name=listing_data.name.lower(),
            )
            db.add(new_listing)

            await db.flush()

            if listing_data.image_urls:
                db.add_all(
                    [
                        ListingImage(listing_id=new_listing.id, image_url=image_url)
                        for image_url in listing_data.image_urls
                    ]
                )

            await db.commit()
            await db.refresh(new_listing)

            return CreateListingResponse(
                id=new_listing.id,
                name=new_listing.name,
                sender_id=new_listing.sender_id,
                receiver_phone=new_listing.receiver_phone,
                delivery_guy_id=new_listing.delivery_guy_id,
                origin_address=new_listing.origin_address,
                origin_lat=new_listing.origin_lat,
                origin_lng=new_listing.origin_lng,
                dest_address=new_listing.dest_address,
                dest_lat=new_listing.dest_lat,
                dest_lng=new_listing.dest_lng,
                distance_km=new_listing.distance_km,
                weight_kg=new_listing.weight_kg,
                description=new_listing.description,
                offered_fare=new_listing.offered_fare,
                status=new_listing.status.value,
                created_at=new_listing.created_at,
                updated_at=new_listing.updated_at,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    async def get_listings(
        self,
        origin: str | None,
        dest: str | None,
        min_fare: float | None,
        max_fare: float | None,
        min_weight: float | None,
        max_weight: float | None,
        distance_range_km: float | None,
        order_by: int | None,
        page: int,
        db: AsyncSession,
    ) -> list[GetListingsResponse]:
        try:
            if page < 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="page must be greater than or equal to 1",
                )

            query = select(Listing).where(Listing.status == "open")

            if origin:
                query = query.where(Listing.origin_address.ilike(f"%{origin}%"))
            if dest:
                query = query.where(Listing.dest_address.ilike(f"%{dest}%"))
            if min_fare:
                query = query.where(Listing.offered_fare >= min_fare)
            if max_fare:
                query = query.where(Listing.offered_fare <= max_fare)
            if min_weight:
                query = query.where(Listing.weight_kg >= min_weight)
            if max_weight:
                query = query.where(Listing.weight_kg <= max_weight)
            if distance_range_km:
                query = query.where(Listing.distance_km <= distance_range_km)
            if order_by:
                if order_by == 1:
                    query = query.order_by(Listing.created_at.asc())
                elif order_by == 0:
                    query = query.order_by(Listing.created_at.desc())

            result = await db.execute(
                query.offset((page - 1) * 20).limit(20)
            )
            listings = result.scalars().all()

            if len(listings) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No job found matching the criteria",
                )

            return [GetListingsResponse.from_orm(listing) for listing in listings]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    async def get_listing_by_id(self, listing_id: int, db: AsyncSession) -> Listing:
        try:
            listing = await db.get(Listing, listing_id)

            if not listing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Listing not found",
                )

            return listing
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    async def close_listing(self, sender_id: int, listing_id: int, db: AsyncSession):
        try:
            listing = await db.get(Listing, listing_id)

            if not listing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Listing not found",
                )

            if listing.sender_id != sender_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to close this listing",
                )
            
            if listing.status != "open":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This job cannot be closed.",
                )

            listing.status = "closed"
            await db.commit()

            return CloseListingResponse(
                id=listing.id,
                status=listing.status
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
