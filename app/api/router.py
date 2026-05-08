from fastapi import APIRouter

from app.api.router import users

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["users"])