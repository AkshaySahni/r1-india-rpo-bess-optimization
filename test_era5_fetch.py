# -*- coding: utf-8 -*-
"""
ECMWF ERA5 Hourly Reanalysis Fetcher and Profile Generator
Fetches 2021-2023 hourly ERA5 reanalysis data for 4 Indian renewable corridors:
- Rajasthan: 26.9124 N, 70.9000 E
- Gujarat: 23.8500 N, 69.7500 E
- Tamil Nadu: 8.1800 N, 77.5300 E
- Karnataka Solar: 14.1000 N, 77.2700 E / Wind: 14.2200 N, 76.4000 E

Variables retrieved:
- surface_solar_radiation_downwards (ssrd -> GHI W/m2)
- 100m_u_component_of_wind, 100m_v_component_of_wind (u100, v100 -> wind speed 100m)
- 10m_u_component_of_wind, 10m_v_component_of_wind (u10, v10 -> wind speed 10m)
- 2m_temperature (t2m -> temp C)
- surface_pressure (sp -> pressure Pa)
"""

import os
import requests
import pandas as pd
import numpy as np

LAT_LON_MAP = {
    "RJ": {"lat": 26.9124, "lon": 70.9000, "name": "Rajasthan (Jaisalmer)"},
    "GJ": {"lat": 23.8500, "lon": 69.7500, "name": "Gujarat (Khavda)"},
    "TN": {"lat": 8.1800, "lon": 77.5300, "name": "Tamil Nadu (Muppandal)"},
    "KA_solar": {"lat": 14.1000, "lon": 77.2700, "name": "Karnataka Solar (Pavagada)"},
    "KA_wind": {"lat": 14.2200, "lon": 76.4000, "name": "Karnataka Wind (Chitradurga)"}
}

YEARS = [2021, 2022, 2023]
RAW_DIR = "data/raw/era5"
os.makedirs(RAW_DIR, exist_ok=True)

def fetch_era5_corridor_year(state_key, year):
    info = LAT_LON_MAP[state_key]
    lat, lon = info["lat"], info["lon"]
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": [
            "shortwave_radiation_instant", # GHI in W/m2
            "wind_speed_10m",             # 10m wind speed m/s
            "wind_speed_100m",            # 100m wind speed m/s
            "temperature_2m",             # 2m temperature C
            "surface_pressure"            # surface pressure hPa
        ],
        "timezone": "Asia/Kolkata"         # IST UTC+5:30 natively
    }
    
    csv_file = os.path.join(RAW_DIR, f"era5_{state_key}_{year}.csv")
    if os.path.exists(csv_file):
        print(f"[CACHE] Loaded {csv_file}")
        return pd.read_csv(csv_file)
        
    print(f"[FETCHING ERA5] {info['name']} for Year {year}...", flush=True)
    resp = requests.get(url, params=params, timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        hourly = data["hourly"]
        df = pd.DataFrame({
            "time_ist": hourly["time"],
            "ghi_w_m2": hourly["shortwave_radiation_instant"],
            "wind_10m_m_s": hourly["wind_speed_10m"],
            "wind_100m_m_s": hourly["wind_speed_100m"],
            "temp_2m_c": hourly["temperature_2m"],
            "pressure_hpa": hourly["surface_pressure"]
        })
        df.to_csv(csv_file, index=False)
        print(f"[SUCCESS] Saved {csv_file} ({len(df)} rows)")
        return df
    else:
        print(f"[ERROR] Failed to fetch ERA5 for {state_key} {year}: {resp.status_code} {resp.text}")
        return None

if __name__ == "__main__":
    for st in LAT_LON_MAP:
        for y in YEARS:
            fetch_era5_corridor_year(st, y)
