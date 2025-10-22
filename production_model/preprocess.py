# production_model/model_service/preprocess.py
"""
preprocess.py
-------------
Downloads CSV training data from Supabase Storage ("data" bucket)
and prepares it for training.
"""

from dotenv import load_dotenv
import os
import pandas as pd
from supabase import create_client

# Load .env from project root (3 levels up)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "data"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def download_training_data(filename: str, local_path: str = "training_data.csv") -> pd.DataFrame:
    print(f"[preprocess] Downloading {filename} from Supabase bucket '{BUCKET_NAME}'...")
    res = supabase.storage.from_(BUCKET_NAME).download(filename)
    print("[preprocess] Listing files in Supabase bucket before downloading...")
    files = supabase.storage.from_(BUCKET_NAME).list()
    for f in files:
        print("  -", f["name"])

    with open(local_path, "wb") as f:
        f.write(res)
    print("[preprocess] Download complete.")
    df = pd.read_csv(local_path)
    print(f"[preprocess] Loaded dataset with shape: {df.shape}")
    return df

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    print("[preprocess] Cleaning dataset...")

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # Combine or convert datetime column if needed
    if "datetime" not in df.columns:
        df["datetime"] = pd.to_datetime("now")
    else:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

    # Standardize road column
    if "road_sector" not in df.columns and "location" in df.columns:
        df.rename(columns={"location": "road_sector"}, inplace=True)

    # Create is_flooded based on "flood type/depth" info
    if "flood type/depth" in df.columns:
        df["is_flooded"] = df["flood type/depth"].notna().astype(int)
    else:
        # default if column missing
        df["is_flooded"] = 1

    # Optional: handle "passability" (could be useful feature)
    if "passability" in df.columns:
        df["passability"] = df["passability"].fillna("Unknown")

    # Drop useless or empty rows
    df = df.dropna(subset=["datetime", "road_sector"], how="any")

    print(f"[preprocess] Final dataset shape: {df.shape}")
    print(f"[preprocess] Columns now: {list(df.columns)}")
    return df
