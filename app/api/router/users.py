from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.services.users_service import UserService
from app.schemas.users import CreateUserRequest, CreateUserResponse, UpdateMeRequest, UpdateMeResponse
from app.core.current_user import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/signup", response_model=CreateUserResponse)
async def signup(user_data: CreateUserRequest, db: AsyncSession = Depends(get_session)):
    service = UserService()
    return await service.create_user(user_data, db)


@router.patch("/me", response_model=UpdateMeResponse)
async def update_me(
    user_data: UpdateMeRequest,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = UserService()
    return await service.update_me(current_user, user_data, db)
