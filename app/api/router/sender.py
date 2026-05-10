from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.core.current_user import get_current_user
from app.models.user import User
from app.schemas.interests import InterestedDeliveryGuyResponse, SelectInterestRequest, SelectInterestResponse, WithdrawInterestRequest, WithdrawInterestResponse
from app.services.interest_service import InterestService

router = APIRouter()

@router.get("/interests", response_model=list[InterestedDeliveryGuyResponse])
async def get_interests(
    listing_id: int,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[InterestedDeliveryGuyResponse]:
    service = InterestService()
    return await service.get_interests(user.id, listing_id, db)

@router.post("/interests/select", response_model=SelectInterestResponse)
async def select_delivery_guy(
    payload: SelectInterestRequest,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> SelectInterestResponse:
    service = InterestService()
    return await service.select_delivery_guy(payload.interest_id, user.id, db)

@router.post("/interest/sender/withdraw", response_model=WithdrawInterestResponse)
async def withdraw_interest(
    payload: WithdrawInterestRequest,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> WithdrawInterestResponse:
    service = InterestService()
    return await service.withdraw_interest_sender(payload.interest_id, user.id, db)
