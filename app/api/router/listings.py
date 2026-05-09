from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.current_user import get_current_user
from app.database.connection import get_session
from app.models.user import User
from app.schemas.listings import CreateListingRequest, CreateListingResponse
from app.services.listings_service import ListingService

router = APIRouter()


@router.post("/create", response_model=CreateListingResponse)
async def create_listing(
    listing_data: CreateListingRequest,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = ListingService()
    return await service.create_listing(listing_data, current_user, db)
