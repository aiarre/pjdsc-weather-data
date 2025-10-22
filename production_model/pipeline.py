# production_model/model_service/pipeline.py
"""
pipeline.py
------------
Automates the entire flood model training pipeline:
1. (Optional) Fetch data (scraper.py)
2. Download training CSV from Supabase
3. Preprocess it
4. Train model
5. Upload trained .pkl to Supabase
"""

from scraper import fetch_latest_data
from preprocess import download_training_data, clean_dataset
from trainer import train_model

def run_pipeline():
    print("[pipeline] Starting flood prediction training pipeline...")
    fetch_latest_data()
    df = download_training_data("flooded_roads_phase1.csv")
    df_clean = clean_dataset(df)
    train_model(df_clean)
    print("[pipeline] ✅ Pipeline completed successfully.")

if __name__ == "__main__":
    run_pipeline()
