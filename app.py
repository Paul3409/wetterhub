import streamlit as st

st.set_page_config(page_title="NOAA Wetterkarten-Generator", layout="centered")

st.title("🗺️ Historischer Wetterkarten-Generator")
st.write("Wählen Sie ein Jahr und einen Monat, um die offizielle NOAA-Wetterkarte (1836–2015) aufzurufen.")

# Eingabemaske für den Nutzer
jahr = st.number_input("Jahr eingeben (1836 - 2015):", min_value=1836, max_value=2015, value=1976, step=1)

monate_dict = {
    "Januar": "1", "Februar": "2", "März": "3", "April": "4",
    "Mai": "5", "Juni": "6", "Juli": "7", "August": "8",
    "September": "9", "Oktober": "10", "November": "11", "Dezember": "12"
}
monat_name = st.selectbox("Monat auswählen:", list(monate_dict.keys()))
monat_num = monate_dict[monat_name]

variable = st.selectbox("Wetter-Parameter:", [
    "Sea Level Pressure (Bodendruck / Isobaren)", 
    "Air Temperature (Lufttemperatur 2m)"
])

# Variablen-Kürzel für die NOAA-Schnittstelle zuweisen
var_code = "prmsl" if "Pressure" in variable else "air"

if st.button("Wetterkarte generieren"):
    # Generierung der exakten NOAA-Plot-URL basierend auf den Nutzereingaben
    noaa_url = (
        f"https://noaa.gov?"
        f"year={jahr}&month={monat_num}&year2={jahr}&month2={monat_num}&"
        f"variable={var_code}&level=1000&type=mean&proj=custom&"
        f"lat1=35&lat2=65&lon1=-10&lon2=30&label=yes&color=yes&icedata=no"
    )
    
    st.success(f"Karte für {monat_name} {jahr} wurde berechnet!")
    st.markdown(f"[**👉 HIER KLICKEN: NOAA-Wetterkarte anzeigen**]({noaa_url})")
    st.info("Hinweis: Da die NOAA die Grafiken live auf ihren US-Servern rendert, öffnet sich die Karte aus Sicherheits- und Performancegründen in einem neuen Tab.")
