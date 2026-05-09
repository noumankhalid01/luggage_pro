from pydantic import BaseModel, EmailStr

class InterestRequest(BaseModel):
    listing_id: int

class InterestResponse(BaseModel):
    id: int
    listing_id: int
    delivery_guy_id: int
    status: str

class InterestedDeliveryGuyResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str

    class Config:
        from_attributes = True