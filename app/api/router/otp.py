from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.current_user import get_current_user
from app.database.connection import get_session
from app.models.user import User
from app.schemas.otp_events import SendOtpRequest, SendOtpResponse, VerifyOtpRequest, VerifyOtpResponse
from app.services.otp_service import OtpService

router = APIRouter()


@router.post("/pickup", response_model=SendOtpResponse)
async def send_pickup_otp(
    payload: SendOtpRequest,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> SendOtpResponse:
    service = OtpService()
    return await service.send_pickup_otp(payload, current_user, db)

@router.post("/verify", response_model=VerifyOtpResponse)
async def verify_otp(
    payload: VerifyOtpRequest,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> VerifyOtpResponse:
    service = OtpService()
    return await service.verify_otp(payload, current_user, db)
