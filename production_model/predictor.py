# production_model/model_service/predictor.py
"""
predictor.py
------------
Loads the trained model (.pkl) from Supabase and predicts flood probability
for given weather and road input.
"""

from dotenv import load_dotenv
import os
import joblib
import numpy as np
from io import BytesIO
from supabase import create_client

# Load .env from project root (3 levels up)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "data"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_model():
    print("[predictor] Downloading model from Supabase...")
    data = supabase.storage.from_(BUCKET_NAME).download("best_flood_model.pkl")
    model = joblib.load(BytesIO(data))
    print("[predictor] Model loaded successfully.")
    return model

def predict_flood_probability(model, weather_data: dict):
    feature_names = [
        "main.temp", "main.humidity", "main.pressure", "rain1h", "wind.speed",
        "hour", "day_of_week", "month", "is_weekend"
    ]
    feat_vector = np.array([[weather_data.get(f, 0) for f in feature_names]])
    prob = model.predict_proba(feat_vector)[0, 1]
    print(f"[predictor] Flood probability: {prob:.3f}")
    return float(prob)
