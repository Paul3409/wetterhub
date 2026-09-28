import streamlit as st

st.set_page_config(page_title="NOAA Wetterkarten-Viewer", layout="wide")

st.title("🗺️ Historischer Wetterkarten-Viewer (1836–2015)")
st.write("Die Karten werden live vom NOAA-Server geladen und direkt hier angezeigt.")

# Eingabe-Bereich in einer Seitenleiste (Sidebar) für mehr Platz
with st.sidebar:
    st.header("⚙️ Einstellungen")
    jahr = st.number_input("Jahr (1836 - 2015):", min_value=1836, max_value=2015, value=1976, step=1)

    monate_dict = {
        "Januar": "1", "Februar": "2", "März": "3", "April": "4",
        "Mai": "5", "Juni": "6", "Juli": "7", "August": "8",
        "September": "9", "Oktober": "10", "November": "11", "Dezember": "12"
    }
    monat_name = st.selectbox("Monat:", list(monate_dict.keys()))
    monat_num = monate_dict[monat_name]

    variable = st.selectbox("Wetter-Parameter:", [
        "Sea Level Pressure (Bodendruck / Isobaren)", 
        "Air Temperature (Lufttemperatur 2m)"
    ])

# Variablen-Kürzel für die NOAA-Schnittstelle zuweisen
var_code = "prmsl" if "Pressure" in variable else "air"

# Die Basis-URL für das Bild generieren
# Wir nutzen hier direkt das CGI-Skript der NOAA, das bei korrekten Parametern das Bild ausgibt
noaa_img_url = (
    f"https://noaa.gov?"
    f"year={jahr}&month={monat_num}&year2={jahr}&month2={monat_num}&"
    f"variable={var_code}&level=1000&type=mean&proj=custom&"
    f"lat1=35&lat2=65&lon1=-10&lon2=30&label=yes&color=yes&icedata=no&action=Create+Plot"
)

# Karte direkt in Streamlit ausgeben
st.subheader(f"Wetterlage für Europa: {monat_name} {jahr}")
st.image(noaa_img_url, caption=f"Quelle: NOAA 20th Century Reanalysis (V3) - {variable}", use_container_width=True)
