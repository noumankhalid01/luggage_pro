from dis import dis
from datetime import datetime

from pydantic import BaseModel


class CreateListingRequest(BaseModel):
    name: str
    receiver_phone: str
    origin_address: str
    origin_lat: float
    origin_lng: float
    dest_address: str
    dest_lat: float
    dest_lng: float
    distance_km: float
    weight_kg: float
    description: str | None = None
    offered_fare: float


class CreateListingResponse(BaseModel):
    id: int
    sender_id: int
    name: str
    receiver_phone: str
    delivery_guy_id: int | None
    origin_address: str
    origin_lat: float
    origin_lng: float
    dest_address: str
    dest_lat: float
    dest_lng: float
    distance_km: float
    weight_kg: float
    description: str | None
    offered_fare: float
    status: str
    created_at: datetime
    updated_at: datetime
