import googlemaps
import os
from dotenv import load_dotenv

load_dotenv()

gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

def get_distance_km(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> float:
    result = gmaps.distance_matrix(
        origins=[(origin_lat, origin_lng)],
        destinations=[(dest_lat, dest_lng)],
        mode="driving"
    )
    km_res = result["rows"][0]["elements"][0]["distance"]["text"]
    km = km_res.split()[0]
    
    return float(km)