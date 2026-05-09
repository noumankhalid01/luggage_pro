from pydantic import BaseModel

class CalculateFareRequest(BaseModel):
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float
    weight_kg: float

class CalculateFareResponse(BaseModel):
    fare: float