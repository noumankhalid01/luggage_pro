from unicodedata import name
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import Listing
from app.models.user import User
from app.schemas.listings import CreateListingRequest, CreateListingResponse
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

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
