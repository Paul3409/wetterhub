import pandas as pd
import numpy as np

INPUT_FILE = "ensemble_raw.csv"
OUTPUT_FILE = "ensemble_final.csv"

def main():
    df = pd.read_csv(INPUT_FILE, parse_dates=["time"])
    
    gfs_cols = [c for c in df.columns if c.startswith("gfs_")]
    aifs_cols = [c for c in df.columns if c.startswith("aifs_")]
    
    print(f"GFS Member: {len(gfs_cols)}, AIFS Member: {len(aifs_cols)}")
    
    # Mittelwert über alle Zeitschritte für Sortierung
    gfs_means = df[gfs_cols].mean()
    aifs_means = df[aifs_cols].mean()
    
    # Nach Mittelwert sortieren
    gfs_sorted = gfs_means.sort_values().index.tolist()
    aifs_sorted = aifs_means.sort_values().index.tolist()
    
    # Pairing: GFS Member i mit AIFS Member i
    n_pairs = min(len(gfs_sorted), len(aifs_sorted))
    paired = {}
    for i in range(n_pairs):
        gfs_col = gfs_sorted[i]
        aifs_col = aifs_sorted[i]
        # Gepaarter Member = Mittelwert der beiden
        paired[f"pair_{i+1:02d}"] = (df[gfs_col] + df[aifs_col]) / 2
    
    # Extras: AIFS Member, die übrig bleiben
    extras = {}
    for i in range(n_pairs, len(aifs_sorted)):
        aifs_col = aifs_sorted[i]
        extras[f"extra_{i-n_pairs+1:02d}"] = df[aifs_col]
    
    # Zusammensetzen
    result = pd.DataFrame({"time": df["time"]})
    for name, series in paired.items():
        result[name] = series
    for name, series in extras.items():
        result[name] = series
    
    result.to_csv(OUTPUT_FILE, index=False)
    n_paired = len(paired)
    n_extra = len(extras)
    print(f"Erstellt: {n_paired} gepaarte + {n_extra} Extras = {n_paired + n_extra} Linien")
    print(f"Gespeichert: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
