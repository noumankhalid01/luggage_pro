from enum import Enum

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.current_user import get_current_user
from app.database.connection import get_session
from app.models.user import User
from app.schemas.listings import CreateListingRequest, CreateListingResponse, GetListingsResponse
from app.services.listings_service import ListingService

router = APIRouter()

class ListingOrderBy(int, Enum):
    created_at_asc = 1
    created_at_desc = 0

@router.post("/create", response_model=CreateListingResponse)
async def create_listing(
    listing_data: CreateListingRequest,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = ListingService()
    return await service.create_listing(listing_data, current_user, db)

@router.get("/data")
async def get_listings(
    origin: str | None = None,
    dest: str | None = None,
    min_fare: float | None = None,
    max_fare: float | None = None,
    min_weight: float | None = None,
    max_weight: float | None = None,
    distance_range_km: float | None = None,
    order_by: ListingOrderBy | None = None,
    db: AsyncSession = Depends(get_session),
) -> list[GetListingsResponse]:
    service = ListingService()
    return await service.get_listings(origin, dest, min_fare, max_fare, min_weight, max_weight, distance_range_km, order_by, db)
