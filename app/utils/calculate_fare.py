async def calculate_fare(distance_km: float, weight_kg: float) -> float:
    distance_fare = distance_km * 20
    weight_fare = weight_kg * 10
    total_fare = distance_fare + weight_fare
    return round(total_fare, 2)