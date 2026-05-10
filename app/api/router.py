from fastapi import APIRouter

from app.api.router import users
from app.api.router import auth
from app.api.router import utils
from app.api.router import listings
from app.api.router import fare
from app.api.router import sender
from app.api.router import traveller

router = APIRouter()

router.include_router(utils.router, prefix="/utils", tags=["utils"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(listings.router, prefix="/listings", tags=["listings"])
router.include_router(fare.router, prefix="/fare", tags=["fare_calculation"])
router.include_router(sender.router, prefix="/listings", tags=["sender"])
router.include_router(traveller.router, prefix="/listings", tags=["traveller"])