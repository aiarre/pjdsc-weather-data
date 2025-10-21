from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from datetime import datetime
from geopy.geocoders import Nominatim

# Load CSV
road_data = pd.read_csv('../data/interim/flooded_roads_phase1.csv')

geolocator = Nominatim(user_agent="flood_app")

def reverse_geocode(lat, lon):
    location = geolocator.reverse((lat, lon))
    if location:
        address = location.raw.get('address', {})
        return {
            "city": address.get("city", address.get("town", None)),
            "road": address.get("road", None),
            "neighborhood": address.get("suburb", None),
            "full_address": location.address
        }
    return {}

def calculate_severity_from_csv(city, location):
    subset = road_data[(road_data['City']==city) & (road_data['Location']==location)]
    if subset.empty:
        return {"score": 0, "severity": "No Flood"}
    
    # Simple example mapping
    depth_map = {
        "Gutter Deep": 0.3,
        "Knee Deep": 0.5,
        "Waist Deep": 0.7,
        "Flooded": 1.0
    }
    depth = subset.iloc[-1]['Flood Type/Depth']
    score = depth_map.get(depth, 0)
    if score >= 0.7:
        severity = "Severe"
    elif score >= 0.4:
        severity = "Moderate"
    elif score > 0:
        severity = "Light"
    else:
        severity = "No Flood"
    return {"score": score, "severity": severity}

@api_view(['POST'])
def predictions(request):
    data = request.data
    lat = data.get("latitude")
    lon = data.get("longitude")
    if lat is None or lon is None:
        return Response({"error": "latitude and longitude are required"}, status=status.HTTP_400_BAD_REQUEST)

    area = reverse_geocode(lat, lon)
    prediction = calculate_severity_from_csv(area.get("city"), area.get("road"))

    return Response({
        "area": area,
        "predictions": [prediction],
        "datetime": datetime.now()
    })


@api_view(['GET'])
def roads(request):
    """
    Returns all roads from CSV (for debugging coordinates)
    """
    all_roads = []
    for _, row in road_data.iterrows():
        all_roads.append({
            "road_sector": row.get("Road_Sector", "Unknown"),
            "city": row.get("City", "Unknown"),
            "latitude": row.get("latitude"),
            "longitude": row.get("longitude"),
        })
    return Response(all_roads)
