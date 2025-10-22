# production_model/model_service/trainer.py
"""
trainer.py
-----------
Trains a flood prediction model using preprocessed data,
then saves the best model as:
  - best_flood_model.pkl
  - flood_model_scaler.pkl
  - weather_main_encoder.pkl
  - weather_desc_encoder.pkl
Uploads all artifacts to Supabase Storage.
"""

from dotenv import load_dotenv
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import roc_auc_score, classification_report
from supabase import create_client

# Load .env (3 levels up from this file)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "data"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def train_model(df: pd.DataFrame):
    print("[trainer] Starting model training...")

    # 🧭 Check class distribution
    print("[trainer] Flood label distribution:")
    print(df["is_flooded"].value_counts())

    # 🧪 Handle single-class dataset by adding dummy 0 rows
    if df["is_flooded"].nunique() < 2:
        print("[trainer] ⚠️ Only one class detected — adding dummy 0 class for testing.")
        n_dummy = min(10, len(df))  # add up to 10 dummy rows
        df_dummy = df.sample(n=n_dummy, random_state=42).copy()
        df_dummy["is_flooded"] = 0
        df = pd.concat([df, df_dummy], ignore_index=True)
        print(f"[trainer] Dataset now has class distribution:\n{df['is_flooded'].value_counts()}")

    # 🧩 Feature Engineering
    df["hour"] = df["datetime"].dt.hour
    df["day_of_week"] = df["datetime"].dt.dayofweek
    df["month"] = df["datetime"].dt.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # Ensure columns exist
    for col in ["main.temp", "main.humidity", "main.pressure", "rain1h", "wind.speed"]:
        if col not in df.columns:
            df[col] = np.random.uniform(20, 30, size=len(df))  # mock if missing

    # Handle weather categorical fields
    for col in ["weather.main", "weather.description"]:
        if col not in df.columns:
            df[col] = "Unknown"
        df[col] = df[col].fillna("Unknown")

    le_weather_main = LabelEncoder()
    le_weather_desc = LabelEncoder()
    df["weather_main_encoded"] = le_weather_main.fit_transform(df["weather.main"])
    df["weather_desc_encoded"] = le_weather_desc.fit_transform(df["weather.description"])

    feature_cols = [
        "main.temp",
        "main.humidity",
        "main.pressure",
        "rain1h",
        "wind.speed",
        "hour",
        "day_of_week",
        "month",
        "is_weekend",
        "weather_main_encoded",
        "weather_desc_encoded",
    ]

    X = df[feature_cols].fillna(0)
    y = df["is_flooded"]

    # 🔀 Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ⚖️ Scale for LR
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 🤖 Models
    models = {
        "RandomForest": RandomForestClassifier(
            n_estimators=100, random_state=42, class_weight="balanced"
        ),
        "GradientBoosting": GradientBoostingClassifier(random_state=42),
        "LogisticRegression": LogisticRegression(
            max_iter=1000, class_weight="balanced"
        ),
    }

    best_model, best_auc, best_name = None, 0, ""

    for name, model in models.items():
        if name == "LogisticRegression":
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_proba_raw = model.predict_proba(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba_raw = model.predict_proba(X_test)

        y_proba = y_proba_raw[:, -1]  # safe extraction
        auc = roc_auc_score(y_test, y_proba)
        print(f"[trainer] {name}: AUC={auc:.4f}")
        print(classification_report(y_test, y_pred))

        if auc > best_auc:
            best_model, best_auc, best_name = model, auc, name

    print(f"[trainer] ✅ Best model: {best_name} (AUC={best_auc:.4f})")

    # 💾 Save artifacts
    joblib.dump(best_model, "best_flood_model.pkl")
    joblib.dump(scaler, "flood_model_scaler.pkl")
    joblib.dump(le_weather_main, "weather_main_encoder.pkl")
    joblib.dump(le_weather_desc, "weather_desc_encoder.pkl")

    print("[trainer] Saved model artifacts locally.")

    # ☁️ Upload all artifacts to Supabase
    for file_name in [
        "best_flood_model.pkl",
        "flood_model_scaler.pkl",
        "weather_main_encoder.pkl",
        "weather_desc_encoder.pkl",
    ]:
        with open(file_name, "rb") as f:
            supabase.storage.from_(BUCKET_NAME).upload(
                file_name, f, file_options={"upsert": "true"}  # <- string fix
            )
        print(f"[trainer] Uploaded '{file_name}' to Supabase bucket '{BUCKET_NAME}'.")

    print("[trainer] ✅ All artifacts uploaded successfully.")
    return best_model, best_auc
