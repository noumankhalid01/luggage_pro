from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    user_login: LoginRequest, db: AsyncSession = Depends(get_session)
) -> LoginResponse:
    service = AuthService()
    return await service.login(user_login, db)

@router.post("/refresh_token", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_token: RefreshTokenRequest, db: AsyncSession = Depends(get_session)
) -> RefreshTokenResponse:
    service = AuthService()
    return await service.refresh_token(refresh_token, db)
