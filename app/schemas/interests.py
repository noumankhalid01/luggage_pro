from pydantic import BaseModel

class InterestRequest(BaseModel):
    listing_id: int

class InterestResponse(BaseModel):
    id: int
    listing_id: int
    delivery_guy_id: int
    status: str