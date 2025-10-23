from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="flood_app")

def reverse_geocode(lat, lon):
    """Convert latitude/longitude into human-readable area"""
    try:
        location = geolocator.reverse((lat, lon), timeout=10)
        if not location:
            return None
        addr = location.raw.get("address", {})
        return {
            "city": addr.get("city") or addr.get("town") or addr.get("municipality"),
            "road": addr.get("road"),
            "neighborhood": addr.get("suburb") or addr.get("neighbourhood"),
            "full_address": location.address,
        }
    except Exception as e:
        print("[reverse_geocode] Error:", e)
        return None
