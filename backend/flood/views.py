from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import pandas as pd
import numpy as np
import joblib
from io import BytesIO
from datetime import datetime
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
from supabase import create_client
import threading
import os

# ==========================================================
# Load environment variables
# ==========================================================
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "data"

# ==========================================================
# Initialize Supabase client
# ==========================================================
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================================
# Load CSV (from Supabase or fallback)
# ==========================================================
def load_road_data():
    print("[startup] Downloading flooded_roads_phase1.csv from Supabase...")
    try:
        data = supabase.storage.from_(BUCKET_NAME).download("flooded_roads_phase1.csv")
        df = pd.read_csv(BytesIO(data))
        print(f"[startup] Road data loaded successfully. Shape: {df.shape}")
        return df
    except Exception as e:
        print("[startup] Failed to load from Supabase:", e)
        if os.path.exists("../data/interim/flooded_roads_phase1.csv"):
            print("[startup] Loading local backup CSV...")
            return pd.read_csv("../data/interim/flooded_roads_phase1.csv")
        print("[startup] No data available.")
        return pd.DataFrame()

road_data = load_road_data()

# ==========================================================
# Lazy-load ML model (Render-friendly)
# ==========================================================
model = None
model_lock = threading.Lock()

def load_model():
    global model
    if model is not None:
        return model

    with model_lock:
        if model is not None:  # double-check inside lock
            return model
        print("[model] Downloading best_flood_model.pkl from Supabase...")
        try:
            model_data = supabase.storage.from_(BUCKET_NAME).download("best_flood_model.pkl")
            model = joblib.load(BytesIO(model_data))
            print("[model] Model loaded successfully.")
        except Exception as e:
            print("[model] Failed to load model:", e)
            model = None
    return model

# Optional: preload model in background (won’t block startup)
threading.Thread(target=load_model, daemon=True).start()

# ==========================================================
# Helper functions
# ==========================================================
geolocator = Nominatim(user_agent="flood_app")

def reverse_geocode(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), timeout=10)
        if location:
            address = location.raw.get('address', {})
            return {
                "city": address.get("city", address.get("town", None)),
                "road": address.get("road", None),
                "neighborhood": address.get("suburb", None),
                "full_address": location.address
            }
    except Exception as e:
        print("[reverse_geocode] Error:", e)
    return {}

def calculate_severity_from_csv(city, location):
    subset = road_data[(road_data['City'] == city) & (road_data['Location'] == location)]
    if subset.empty:
        return {"score": 0, "severity": "No Flood"}
    
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

# ==========================================================
# Django REST API Views
# ==========================================================

@api_view(['POST'])
def predict(request):
    """
    Predict flood probability and estimate severity.
    """
    data = request.data
    lat = data.get("latitude")
    lon = data.get("longitude")

    if lat is None or lon is None:
        return Response({"error": "latitude and longitude are required"}, status=status.HTTP_400_BAD_REQUEST)

    area = reverse_geocode(lat, lon)
    severity_info = calculate_severity_from_csv(area.get("city"), area.get("road"))

    # Load model on demand
    model_instance = load_model()

    flood_prob = None
    if model_instance is not None and all(k in data for k in [
        "main_temp", "main_humidity", "main_pressure", "rain1h", "wind_speed",
        "hour", "day_of_week", "month", "is_weekend"
    ]):
        features = np.array([[
            data["main_temp"],
            data["main_humidity"],
            data["main_pressure"],
            data["rain1h"],
            data["wind_speed"],
            data["hour"],
            data["day_of_week"],
            data["month"],
            data["is_weekend"]
        ]])
        flood_prob = float(model_instance.predict_proba(features)[0, 1])

    return Response({
        "area": area,
        "severity": severity_info,
        "ai_probability": flood_prob,
        "timestamp": datetime.now().isoformat()
    })


@api_view(['GET'])
def roads(request):
    """
    Returns all roads from CSV (for debugging)
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


@api_view(['POST'])
def retrain(request):
    """
    Retrains the model using the AI pipeline and reloads it.
    """
    from .pipeline import run_pipeline
    global model
    try:
        run_pipeline()
        model = None
        load_model()  # reload after retrain
        return JsonResponse({"status": "success", "message": "Model retrained and reloaded."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
