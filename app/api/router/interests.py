from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.core.current_user import get_current_user
from app.models.user import User
from app.schemas.interests import InterestRequest, InterestResponse
from app.services.interest_service import InterestService

router = APIRouter()

@router.post("/interest", response_model=InterestResponse)
async def express_interest(
    interest_request: InterestRequest,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> InterestResponse:
    service = InterestService()
    return await service.express_interest(interest_request.listing_id, user.id, db)