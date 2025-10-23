# 🌧️ Flood Prediction Model — PJDSC Weather Data

A machine learning pipeline that predicts road flooding based on weather and location data.  
This project automatically downloads training data from **Supabase Storage**, trains a predictive model, and uploads the trained model (`.pkl`) back to Supabase.  
It is designed to run both locally and on **Render** for automated retraining.

---

## 📁 Project Structure

```
pjdsc-weather-data/
├── .env
├── README.md
├── frontend/
├── backend/
└── model/

```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd pjdsc-weather-data
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:

```bash
SUPABASE_URL=https://<your-project>.supabase.co
SUPABASE_KEY=<your-service-role-key>
```

> ⚠️ Use the **Service Role Key**, not the public anon key.

---

## ☁️ Supabase Setup

1. Go to [Supabase Dashboard](https://supabase.com/dashboard).  
2. Create a **Storage Bucket** named `data`.  
3. Upload your training CSV (e.g. `flooded_roads_phase1.csv`) to the bucket root.  
4. Ensure the bucket allows read/write access for your service role key.

Example file list:
```
data/
├── flooded_roads_phase1.csv
├── weather_all_months.csv
└── best_flood_model.pkl   ← auto-uploaded after training
```

---

## 🚀 Running the Pipeline Locally

```bash
cd model/reuter/model_service
python pipeline.py
```

If successful, you’ll see logs like:
```
[preprocess] Downloading flooded_roads_phase1.csv...
[trainer] ✅ Best model: RandomForest (AUC=0.92)
[trainer] Uploaded 'best_flood_model.pkl' to Supabase.
```

The trained model (`best_flood_model.pkl`) will appear in your Supabase bucket automatically.

---

## 🧠 Components Overview

| File | Purpose |
|------|----------|
| **scraper.py** | Placeholder for automated weather/flood scraping. |
| **preprocess.py** | Downloads and cleans CSV data from Supabase. |
| **trainer.py** | Trains the ML model (RandomForest, GradientBoosting, etc.) and uploads results. |
| **predictor.py** | Loads `.pkl` model from Supabase and predicts flood probability. |
| **pipeline.py** | Orchestrates the full process: download → clean → train → upload. |

---

## 🧪 Example Prediction (after training)

```python
from predictor import load_model, predict_flood_probability

model = load_model()
sample_input = {
    "main.temp": 30.5,
    "main.humidity": 85,
    "main.pressure": 1002,
    "rain1h": 12,
    "wind.speed": 3.2,
    "hour": 15,
    "day_of_week": 2,
    "month": 8,
    "is_weekend": 0
}
prob = predict_flood_probability(model, sample_input)
print("Flood probability:", prob)
```

---

## 🛠️ Deployment to Render

1. Connect this repo to [Render.com](https://render.com).  
2. Create a **Web Service** or **Cron Job** (if you only need periodic retraining).  
3. Add the `.env` variables (same as local).  
4. Command to run training:
   ```bash
   python model/reuter/model_service/pipeline.py
   ```

---

## 🧩 Notes

- The model artifacts are stored in Supabase Storage (`data` bucket).
- Training datasets should be CSV files with at least:
  ```
  datetime, Location, Flood Type/Depth, Passability, Road_Sector
  ```
- `clean_dataset()` automatically infers the flood flag (`is_flooded`) from the data.

---

## 👨‍💻 Collaborators
**Leanne Mariz Austria**  
UP Diliman — BS Computer Science  

**John Mark Palpal-latoc**  
UP Diliman — BS Computer Science  

**Reuter Jan Camacho**  
UP Diliman — BS Computer Science  

**Nicanor Froilan Pascual**  
UP Diliman — BS Computer Science  
