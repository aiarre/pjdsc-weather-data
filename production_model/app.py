from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from io import BytesIO
import joblib
import numpy as np
from supabase import create_client
from dotenv import load_dotenv

from .pipeline import run_pipeline

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "data"

# Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------
# FastAPI app with /api root
# -------------------------------
app = FastAPI(
    title="Flood Prediction AI Microservice",
    root_path="/api"  # all endpoints will be under /api
)

# -------------------------------
# Request model
# -------------------------------
class FloodFeatures(BaseModel):
    main_temp: float
    main_humidity: float
    main_pressure: float
    rain1h: float
    wind_speed: float
    hour: int
    day_of_week: int
    month: int
    is_weekend: int

# -------------------------------
# Load model
# -------------------------------
def load_model():
    print("[startup] Downloading model from Supabase...")
    try:
        data = supabase.storage.from_(BUCKET_NAME).download("best_flood_model.pkl")
        model = joblib.load(BytesIO(data))
        print("[startup] Model loaded successfully.")
        return model
    except Exception as e:
        print("[startup] Failed to load model:", e)
        return None

model = load_model()

# -------------------------------
# Endpoints
# -------------------------------
@app.get("/")
def root():
    return {"status": "ok", "message": "Flood AI microservice is running!"}

@app.post("/predict")
def predict(features: FloodFeatures):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available")
    
    feat_vector = np.array([[
        features.main_temp,
        features.main_humidity,
        features.main_pressure,
        features.rain1h,
        features.wind_speed,
        features.hour,
        features.day_of_week,
        features.month,
        features.is_weekend
    ]])
    
    prob = model.predict_proba(feat_vector)[0, 1]
    return {"flood_probability": float(prob)}

@app.post("/retrain")
def retrain_models():
    run_pipeline()
    global model
    model = load_model()  # reload newly trained model
    return {"status": "training completed"}
