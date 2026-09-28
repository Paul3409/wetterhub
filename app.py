import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Mühlberg Ensemble", layout="wide")

# Schwarzer Hintergrund
st.markdown("""
<style>
.stApp {
    background-color: #000000;
}
</style>
""", unsafe_allow_html=True)

st.title("🌡️ Mühlberg/Elbe — Eigenes Ensemble")
st.caption("GFS + AIFS Member-Pairing (nach Extremwerten sortiert)")

@st.cache_data
def load_data():
    df = pd.read_csv("ensemble_final.csv", parse_dates=["time"])
    return df

df = load_data()

paired_cols = [c for c in df.columns if c.startswith("pair_")]
extra_cols = [c for c in df.columns if c.startswith("extra_")]

fig = go.Figure()

# Gepaarte Member (rot)
for col in paired_cols:
    fig.add_trace(go.Scatter(
        x=df["time"], y=df[col],
        mode="lines",
        line=dict(color="rgba(255, 60, 60, 0.4)", width=1),
        name=col,
        showlegend=False,
        hovertemplate=f"<b>{col}</b><br>%{{x}}<br>%{{y:.1f}} °C<extra></extra>"
    ))

# Extras (grün)
for col in extra_cols:
    fig.add_trace(go.Scatter(
        x=df["time"], y=df[col],
        mode="lines",
        line=dict(color="rgba(60, 255, 100, 0.5)", width=1),
        name=col,
        showlegend=False,
        hovertemplate=f"<b>{col}</b><br>%{{x}}<br>%{{y:.1f}} °C<extra></extra>"
    ))

# Mittelwert aller (weiß, dicker)
all_cols = paired_cols + extra_cols
mean_series = df[all_cols].mean(axis=1)
fig.add_trace(go.Scatter(
    x=df["time"], y=mean_series,
    mode="lines",
    line=dict(color="white", width=3),
    name="Mittelwert",
    hovertemplate="<b>Mittelwert</b><br>%{x}<br>%{y:.1f} °C<extra></extra>"
))

fig.update_layout(
    plot_bgcolor="black",
    paper_bgcolor="black",
    font=dict(color="white"),
    xaxis=dict(
        gridcolor="#333333",
        zerolinecolor="#444444",
        title="Zeit"
    ),
    yaxis=dict(
        gridcolor="#333333",
        zerolinecolor="#444444",
        title="Temperatur 2m (°C)"
    ),
    hovermode="x unified",
    legend=dict(
        bgcolor="rgba(0,0,0,0.8)",
        font=dict(color="white")
    ),
    margin=dict(l=40, r=20, t=40, b=40)
)

st.plotly_chart(fig, use_container_width=True, theme=None)

# Info-Zeile
st.caption(f"Gepaarte Member: {len(paired_cols)} (rot) · Extras: {len(extra_cols)} (grün) · Gesamt: {len(paired_cols) + len(extra_cols)} Linien")
