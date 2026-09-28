# Mühlberg/Elbe — Eigenes Ensemble

GFS + AIFS Member-Pairing. T2m. 50 Linien (30 gepaart + 20 Extras).

## Setup

1. Repo klonen
2. `pip install -r requirements.txt`
3. `python fetch_data.py && python process.py`
4. `streamlit run app.py`

## GitHub Action

1. Repo → Actions → „Ensemble Update" → „Run workflow"
2. Wartet ~1 Minute
3. Streamlit liest die committete `ensemble_final.csv`

## Farben
- Rot = gepaarte Member
- Grün = AIFS Extras
- Weiß (dick) = Mittelwert aller 50
