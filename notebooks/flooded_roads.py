#!/usr/bin/env python
# coding: utf-8

"""
Flood Prediction Analysis
Data Science Project: Predicting Road Flooding Based on Weather Conditions

This script analyzes flood data and weather conditions to build a predictive model
for identifying which roads are likely to be flooded given weather conditions.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler, LabelEncoder

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
np.random.seed(42)

print("Libraries imported successfully!")
print(f"Pandas version: {pd.__version__}")
print(f"NumPy version: {np.__version__}")

# --- Load datasets ---
print("Loading datasets...")

flood_df = pd.read_csv("../data/interim/flooded_roads_phase1.csv")
weather_df = pd.read_csv("../data/interim/weather_all_months_hourly.csv")
mmda_df = pd.read_csv("../data/interim/mmda_flooded_roads.csv", on_bad_lines="skip")

print(f"Flood data shape: {flood_df.shape}")
print(f"Weather data shape: {weather_df.shape}")
print(f"MMDA data shape: {mmda_df.shape}")

# --- Data Preprocessing ---
print("Preprocessing data...")

flood_df['datetime'] = pd.to_datetime(flood_df['datetime']).dt.tz_localize('Asia/Singapore')
weather_df['datetime'] = pd.to_datetime(weather_df['datetime'])
weather_df['rain1h'] = pd.to_numeric(weather_df['rain1h'], errors='coerce').fillna(0)

flood_depth_map = {
    'Subsided': 0, 'Half Gutter Deep': 4, 'Gutter Deep': 8, 'Above Gutter Deep': 10,
    'Half Knee Deep': 10, 'Half Tire Deep': 13, 'Knee Deep': 19, 'Tire Deep': 26,
    'Knee-Waist Deep': 25, 'Waist Deep': 37, 'Chest Deep': 45, '4 Feet Deep': 48,
    '6 Feet Deep': 72,
}
flood_df['depth_in'] = flood_df['Flood Type/Depth'].map(flood_depth_map)

# --- Road Sector Analysis ---
sector_counts = flood_df['Road_Sector'].value_counts()
plt.figure(figsize=(15, 8))
sector_counts.plot(kind='bar')
plt.title('Number of Flood Events by Road Sector')
plt.xlabel('Road Sector')
plt.ylabel('Number of Flood Events')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# --- Aggregate worst flood per road/time ---
def get_worst_flood_condition(group):
    return group.loc[group['depth_in'].idxmax()]

flood_aggregated = flood_df.groupby(['datetime', 'Road_Sector']).apply(
    get_worst_flood_condition, include_groups=False
).reset_index()

flood_aggregated['is_flooded'] = (flood_aggregated['depth_in'] > 0).astype(int)
flood_aggregated['datetime_hour'] = flood_aggregated['datetime'].dt.floor('H')
weather_df['datetime_hour'] = weather_df['datetime'].dt.floor('H')

# --- Hourly weather aggregation ---
def fast_transform(series):
    return series.value_counts().idxmax() if not series.empty else 'Unknown'

weather_hourly = weather_df.groupby(['datetime_hour', 'City']).agg({
    'main.temp': 'mean', 'main.feels_like': 'mean', 'main.temp_min': 'min', 'main.temp_max': 'max',
    'main.pressure': 'mean', 'main.humidity': 'mean', 'wind.speed': 'mean', 'wind.gust': 'mean',
    'clouds.all': 'mean', 'rain1h': 'sum',
    'weather.main': fast_transform, 'weather.description': fast_transform
}).reset_index()

# --- City-Road Mapping ---
city_road_mapping = flood_aggregated.groupby('City')['Road_Sector'].apply(list).to_dict()

all_combinations = []
for city in weather_hourly['City'].unique():
    city_roads = city_road_mapping.get(city, [])
    for road in city_roads:
        city_weather = weather_hourly[weather_hourly['City'] == city].copy()
        city_weather['Road_Sector'] = road
        all_combinations.append(city_weather)

weather_expanded = pd.concat(all_combinations, ignore_index=True)

merged_data = weather_expanded.merge(
    flood_aggregated[['datetime_hour', 'Road_Sector', 'is_flooded', 'depth_in']],
    on=['datetime_hour', 'Road_Sector'],
    how='left'
)

merged_data['is_flooded'] = merged_data['is_flooded'].fillna(0).astype(int)
merged_data['depth_in'] = merged_data['depth_in'].fillna(0).astype(int)

# --- Feature Engineering ---
merged_data['hour'] = merged_data['datetime_hour'].dt.hour
merged_data['day_of_week'] = merged_data['datetime_hour'].dt.dayofweek
merged_data['month'] = merged_data['datetime_hour'].dt.month
merged_data['is_weekend'] = (merged_data['day_of_week'] >= 5).astype(int)
merged_data['temp_range'] = merged_data['main.temp_max'] - merged_data['main.temp_min']
merged_data['is_raining'] = (merged_data['rain1h'] > 0).astype(int)
merged_data['heavy_rain'] = (merged_data['rain1h'] > 2.5).astype(int)
merged_data['very_heavy_rain'] = (merged_data['rain1h'] > 5.0).astype(int)

for lag in [1, 2, 3, 6, 12, 24]:
    merged_data[f'rain_lag_{lag}h'] = merged_data.groupby('Road_Sector')['rain1h'].shift(lag).fillna(0)
    merged_data[f'cumulative_rain_{lag}h'] = merged_data.groupby('Road_Sector')['rain1h'].rolling(window=lag, min_periods=1).sum().reset_index(0, drop=True)

for lag in [1, 2, 3, 6]:
    merged_data[f'temp_lag_{lag}h'] = merged_data.groupby('Road_Sector')['main.temp'].shift(lag).fillna(merged_data['main.temp'].mean())
    merged_data[f'humidity_lag_{lag}h'] = merged_data.groupby('Road_Sector')['main.humidity'].shift(lag).fillna(merged_data['main.humidity'].mean())

merged_data['pressure_change_1h'] = merged_data.groupby('Road_Sector')['main.pressure'].diff().fillna(0)
merged_data['pressure_change_3h'] = merged_data.groupby('Road_Sector')['main.pressure'].diff(periods=3).fillna(0)
merged_data['wind_gust_ratio'] = merged_data['wind.gust'] / (merged_data['wind.speed'] + 1e-6)
merged_data['high_wind'] = (merged_data['wind.speed'] > 10).astype(int)

# --- Prepare features ---
feature_cols = [
    'main.temp', 'main.feels_like', 'main.temp_min', 'main.temp_max',
    'main.pressure', 'main.humidity', 'wind.speed', 'wind.gust', 'clouds.all', 'rain1h',
    'hour', 'day_of_week', 'month', 'is_weekend',
    'temp_range', 'is_raining', 'heavy_rain', 'very_heavy_rain',
    'pressure_change_1h', 'pressure_change_3h', 'wind_gust_ratio', 'high_wind',
    'rain_lag_1h', 'rain_lag_2h', 'rain_lag_3h', 'rain_lag_6h', 'rain_lag_12h', 'rain_lag_24h',
    'cumulative_rain_1h', 'cumulative_rain_2h', 'cumulative_rain_3h', 'cumulative_rain_6h', 
    'cumulative_rain_12h', 'cumulative_rain_24h',
    'temp_lag_1h', 'temp_lag_2h', 'temp_lag_3h', 'temp_lag_6h',
    'humidity_lag_1h', 'humidity_lag_2h', 'humidity_lag_3h', 'humidity_lag_6h'
]

le_weather_main = LabelEncoder()
le_weather_desc = LabelEncoder()
merged_data['weather_main_encoded'] = le_weather_main.fit_transform(merged_data['weather.main'])
merged_data['weather_desc_encoded'] = le_weather_desc.fit_transform(merged_data['weather.description'])
feature_cols.extend(['weather_main_encoded', 'weather_desc_encoded'])

road_sector_dummies = pd.get_dummies(merged_data['Road_Sector'])
feature_cols.extend(road_sector_dummies.columns)
for col in feature_cols:
    if col not in merged_data.columns:
        merged_data[col] = 0

X = merged_data[feature_cols].fillna(0)
y = merged_data['is_flooded']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

models = {
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
    'Logistic Regression': LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000)
}

model_results = {}
for name, model in models.items():
    print(f"\nTraining {name}...")
    if name == 'Logistic Regression':
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    auc_score = roc_auc_score(y_test, y_pred_proba)
    model_results[name] = {'model': model, 'predictions': y_pred, 'probabilities': y_pred_proba, 'auc_score': auc_score}
    print(f"{name} - AUC Score: {auc_score:.4f}")

best_model_name = max(model_results.keys(), key=lambda x: model_results[x]['auc_score'])
best_model_obj = model_results[best_model_name]['model']
print(f"Best model: {best_model_name} with AUC: {model_results[best_model_name]['auc_score']:.4f}")

# Save model and preprocessing objects
joblib.dump(best_model_obj, 'best_flood_model.pkl')
joblib.dump(scaler, 'flood_model_scaler.pkl')
joblib.dump(le_weather_main, 'weather_main_encoder.pkl')
joblib.dump(le_weather_desc, 'weather_desc_encoder.pkl')

print("Model and preprocessing objects saved successfully!")
