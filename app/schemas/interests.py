from alembic.util import status
from pydantic import BaseModel, EmailStr

class InterestRequest(BaseModel):
    listing_id: int

class InterestResponse(BaseModel):
    id: int
    listing_id: int
    delivery_guy_id: int
    status: str

class InterestedDeliveryGuyResponse(BaseModel):
    interest_id: int
    delivery_guy_id: int
    full_name: str
    email: EmailStr
    phone: str
    status: str

    class Config:
        from_attributes = True

class SelectInterestRequest(BaseModel):
    interest_id: int

class SelectInterestResponse(BaseModel):
    interest_id: int
    listing_id: int
    delivery_guy_id: int
    status: str

class WithdrawInterestRequest(BaseModel):
    interest_id: int

class WithdrawInterestResponse(BaseModel):
    success: bool