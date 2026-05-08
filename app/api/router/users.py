from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.services.users_service import UserService
from app.schemas.users import CreateUserRequest, CreateUserResponse

router = APIRouter()

@router.post("/signup", response_model=CreateUserResponse)
async def signup(user_data: CreateUserRequest, db: AsyncSession = Depends(get_session)):
    service = UserService()
    return await service.create_user(user_data, db)