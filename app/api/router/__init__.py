from fastapi import APIRouter, Depends

from . import users, auth, utils, listings, fare

router = APIRouter()

router.include_router(utils.router, prefix="/utils", tags=["utils"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(listings.router, prefix="/listings", tags=["listings"])
router.include_router(fare.router, prefix="/fare", tags=["fare_calculation"])
