from fastapi import APIRouter, Depends

from . import users, auth, utils, listings, fare, sender, traveller, otp

router = APIRouter()

router.include_router(utils.router, prefix="/utils", tags=["utils"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(listings.router, prefix="/listings", tags=["listings"])
router.include_router(fare.router, prefix="/fare", tags=["fare_calculation"])
router.include_router(sender.router, prefix="/listings", tags=["sender"])
router.include_router(traveller.router, prefix="/listings", tags=["traveller"])
router.include_router(otp.router, prefix="/otp", tags=["otp"])