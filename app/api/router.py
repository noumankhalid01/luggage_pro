from fastapi import APIRouter

from app.api.router import users
from app.api.router import auth
from app.api.router import utils

router = APIRouter()

router.include_router(utils.router, prefix="/utils", tags=["utils"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])