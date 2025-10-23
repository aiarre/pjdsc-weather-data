import pandas as pd  

floods = pd.read_csv("flooded_roads_phase1_hourly.csv")  
weather = pd.read_csv("weather_all_months_hourly.csv")  

floods["date"] = pd.to_datetime(floods["datetime"]).dt.date  
weather["date"] = pd.to_datetime(weather["datetime"]).dt.date  

merged = pd.merge(
    floods, weather,
    on=["City", "date", "hour"],
    how="inner"
)  

merged.to_csv("floods_with_weather.csv", index=False)  
