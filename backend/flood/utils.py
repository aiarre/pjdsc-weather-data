from datetime import datetime
from geopy.geocoders import Nominatim

def reverse_geocode(lat, lon):
    """
    Convert lat/lon into a general area (city, neighborhood, road)
    """
    geolocator = Nominatim(user_agent="flood_app")
    location = geolocator.reverse((lat, lon))
    if location is None:
        return None
    address = location.raw.get('address', {})
    city = address.get('city') or address.get('town') or address.get('municipality')
    road = address.get('road')
    neighborhood = address.get('suburb') or address.get('neighbourhood')
    return {
        "city": city,
        "road": road,
        "neighborhood": neighborhood,
        "full_address": location.address
    }
