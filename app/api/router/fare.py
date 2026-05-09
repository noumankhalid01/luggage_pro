from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.fare import CalculateFareRequest, CalculateFareResponse
from app.utils.calculate_fare import calculate_fare
from app.utils.maps import get_distance_km
from app.core.current_user import get_current_user

router = APIRouter()

@router.post("/calculate", response_model=CalculateFareResponse)
async def calculate_fare_endpoint(
    request: CalculateFareRequest,
    user = Depends(get_current_user)
):
    try:
        distance_km = get_distance_km(request.origin_lat, request.origin_lng, request.dest_lat, request.dest_lng)
        fare = calculate_fare(distance_km, request.weight_kg)
        return CalculateFareResponse(fare=fare)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )