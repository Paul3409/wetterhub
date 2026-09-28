import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------
LAT = 51.437
LON = 13.201
FORECAST_DAYS = 15
CACHE_FILE = "ensemble_final.csv"

st.set_page_config(page_title="Mühlberg Ensemble", layout="wide")

# Schwarzer Hintergrund
st.markdown("""
<style>
.stApp { background-color: #000000; }
h1, h2, h3, p, div { color: #ffffff; }
</style>
""", unsafe_allow_html=True)

st.title("🌡️ Mühlberg/Elbe — Eigenes Ensemble")
st.caption("GFS + AIFS · Member-Pairing nach Extremwerten · T2m · 360 h")


# ---------------------------------------------------------------------------
# Daten holen
# ---------------------------------------------------------------------------
def fetch_ensemble(model: str):
    url = "https://ensemble-api.open-meteo.com/v1/ensemble"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "hourly": "temperature_2m",
        "models": model,
        "forecast_days": FORECAST_DAYS,
        "timezone": "Europe/Berlin",
    }
    r = requests.get(url, params=params, timeout=120)
    r.raise_for_status()
    return r.json()


def parse_members(data, model_name: str):
    hourly = data["hourly"]
    times = hourly["time"]
    member_keys = [k for k in hourly.keys() if k.startswith("temperature_2m")]

    df = pd.DataFrame({"time": pd.to_datetime(times)})

    for key in member_keys:
        if key == "temperature_2m":
            col_name = f"{model_name}_ctrl"
        else:
            member_num = key.split("member")[-1]
            col_name = f"{model_name}_m{member_num}"
        df[col_name] = hourly[key]

    return df


def build_ensemble():
    """Holt GFS + AIFS, paart nach Extremwerten, gibt finale 50 Linien zurück."""
    gfs_data = fetch_ensemble("gfs025")
    aifs_data = fetch_ensemble("ecmwf_aifs025_ensemble")

    gfs_df = parse_members(gfs_data, "gfs")
    aifs_df = parse_members(aifs_data, "aifs")

    merged = pd.merge(gfs_df, aifs_df, on="time", how="inner")

    gfs_cols = [c for c in merged.columns if c.startswith("gfs_")]
    aifs_cols = [c for c in merged.columns if c.startswith("aifs_")]

    # Sortieren nach Mittelwert über alle Zeitpunkte
    gfs_sorted = merged[gfs_cols].mean().sort_values().index.tolist()
    aifs_sorted = merged[aifs_cols].mean().sort_values().index.tolist()

    n_pairs = min(len(gfs_sorted), len(aifs_sorted))

    result = pd.DataFrame({"time": merged["time"]})

    # Gepaarte Member
    for i in range(n_pairs):
        gfs_col = gfs_sorted[i]
        aifs_col = aifs_sorted[i]
        result[f"pair_{i+1:02d}"] = (merged[gfs_col] + merged[aifs_col]) / 2

    # Extras (übrige AIFS Member)
    for i in range(n_pairs, len(aifs_sorted)):
        aifs_col = aifs_sorted[i]
        result[f"extra_{i-n_pairs+1:02d}"] = merged[aifs_col]

    return result


# ---------------------------------------------------------------------------
# Sidebar: Daten erzeugen
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Daten")
    if st.button("🔄 Ensemble jetzt erzeugen", use_container_width=True):
        with st.spinner("Lade GFS + AIFS von Open-Meteo..."):
            try:
                df_new = build_ensemble()
                df_new.to_csv(CACHE_FILE, index=False)
                st.cache_data.clear()
                st.success(f"Fertig: {df_new.shape[1]-1} Linien, {df_new.shape[0]} Zeitpunkte")
                st.rerun()
            except Exception as e:
                st.error(f"Fehler: {e}")

    if os.path.exists(CACHE_FILE):
        mtime = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
        st.caption(f"Letzte Erzeugung: {mtime:%Y-%m-%d %H:%M}")
    else:
        st.warning("Noch keine Daten. Bitte oben klicken.")


# ---------------------------------------------------------------------------
# Daten laden
# ---------------------------------------------------------------------------
if not os.path.exists(CACHE_FILE):
    st.info("👉 Bitte links auf **'Ensemble jetzt erzeugen'** klicken.")
    st.stop()


@st.cache_data
def load_data():
    return pd.read_csv(CACHE_FILE, parse_dates=["time"])


df = load_data()

paired_cols = [c for c in df.columns if c.startswith("pair_")]
extra_cols = [c for c in df.columns if c.startswith("extra_")]


# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
fig = __import__("plotly.graph_objects", fromlist=["go"]).Figure()

import plotly.graph_objects as go  # noqa: E402

fig = go.Figure()

# Gepaarte Member (rot)
for col in paired_cols:
    fig.add_trace(go.Scatter(
        x=df["time"], y=df[col],
        mode="lines",
        line=dict(color="rgba(255, 60, 60, 0.4)", width=1),
        name=col,
        showlegend=False,
        hovertemplate=f"<b>{col}</b><br>%{{x}}<br>%{{y:.1f}} °C<extra></extra>",
    ))

# Extras (grün)
for col in extra_cols:
    fig.add_trace(go.Scatter(
        x=df["time"], y=df[col],
        mode="lines",
        line=dict(color="rgba(60, 255, 100, 0.5)", width=1),
        name=col,
        showlegend=False,
        hovertemplate=f"<b>{col}</b><br>%{{x}}<br>%{{y:.1f}} °C<extra></extra>",
    ))

# Mittelwert aller (weiß, dicker)
all_cols = paired_cols + extra_cols
mean_series = df[all_cols].mean(axis=1)
fig.add_trace(go.Scatter(
    x=df["time"], y=mean_series,
    mode="lines",
    line=dict(color="white", width=3),
    name="Mittelwert",
    hovertemplate="<b>Mittelwert</b><br>%{x}<br>%{y:.1f} °C<extra></extra>",
))

fig.update_layout(
    plot_bgcolor="black",
    paper_bgcolor="black",
    font=dict(color="white"),
    xaxis=dict(gridcolor="#333333", zerolinecolor="#444444", title="Zeit"),
    yaxis=dict(gridcolor="#333333", zerolinecolor="#444444", title="Temperatur 2m (°C)"),
    hovermode="x unified",
    legend=dict(bgcolor="rgba(0,0,0,0.8)", font=dict(color="white")),
    margin=dict(l=40, r=20, t=40, b=40),
)

st.plotly_chart(fig, width="stretch")

st.caption(
    f"Gepaarte Member: {len(paired_cols)} (rot) · "
    f"Extras: {len(extra_cols)} (grün) · "
    f"Gesamt: {len(paired_cols) + len(extra_cols)} Linien"
        )
