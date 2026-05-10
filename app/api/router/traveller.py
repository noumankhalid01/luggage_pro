from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.core.current_user import get_current_user
from app.models.user import User
from app.schemas.interests import InterestRequest, InterestResponse, WithdrawInterestRequest, WithdrawInterestResponse 
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


@router.post("/interest/traveller/withdraw", response_model=WithdrawInterestResponse)
async def withdraw_interest(
    payload: WithdrawInterestRequest,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> WithdrawInterestResponse:
    service = InterestService()
    return await service.withdraw_interest_traveller(payload.interest_id, user.id, db)
