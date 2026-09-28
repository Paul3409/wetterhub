import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime

LAT = 51.437
LON = 13.201
FORECAST_DAYS = 15  # 360h
OUTPUT_FILE = "ensemble_raw.csv"

def fetch_ensemble(model: str):
    """Holt alle Member eines Modells von Open-Meteo."""
    url = "https://ensemble-api.open-meteo.com/v1/ensemble"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "hourly": "temperature_2m",
        "models": model,
        "forecast_days": FORECAST_DAYS,
        "timezone": "Europe/Berlin"
    }
    r = requests.get(url, params=params, timeout=120)
    r.raise_for_status()
    return r.json()

def parse_members(data, model_name: str):
    """Extrahiert alle Member als separate Spalten."""
    hourly = data["hourly"]
    times = hourly["time"]
    
    # Finde alle Keys, die mit "temperature_2m" beginnen
    member_keys = [k for k in hourly.keys() if k.startswith("temperature_2m")]
    
    df = pd.DataFrame({"time": pd.to_datetime(times)})
    
    for key in member_keys:
        # Member-Name: "temperature_2m" (control) oder "temperature_2m_member01"
        if key == "temperature_2m":
            col_name = f"{model_name}_ctrl"
        else:
            member_num = key.split("member")[-1]
            col_name = f"{model_name}_m{member_num}"
        df[col_name] = hourly[key]
    
    return df

def main():
    print("Lade GFS Ensemble...")
    gfs_data = fetch_ensemble("gfs025")
    gfs_df = parse_members(gfs_data, "gfs")
    print(f"  GFS Member: {len([c for c in gfs_df.columns if c != 'time'])}")
    
    print("Lade AIFS Ensemble...")
    aifs_data = fetch_ensemble("ecmwf_aifs025_ensemble")
    aifs_df = parse_members(aifs_data, "aifs")
    print(f"  AIFS Member: {len([c for c in aifs_df.columns if c != 'time'])}")
    
    # Zusammenführen auf gemeinsame Zeitachse
    merged = pd.merge(gfs_df, aifs_df, on="time", how="inner")
    merged.to_csv(OUTPUT_FILE, index=False)
    print(f"Gespeichert: {OUTPUT_FILE} ({merged.shape})")

if __name__ == "__main__":
    main()
