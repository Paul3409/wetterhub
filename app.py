import streamlit as st
import pandas as pd
import numpy as np

st.title("️ Mein Langfrist-Wettermodell (1836 - 2015)")
st.write("Vergleichen Sie aktuelle Monate mit der NOAA-Datenbank, um Analogjahre zu finden.")

# Datei-Uploader für Ihre exportierte NOAA-CSV
uploaded_file = st.file_file_uploader("Laden Sie Ihre NOAA-CSV-Datei hoch", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Daten erfolgreich geladen!", df.head())
    
    # Filter für das Ziel-Jahr
    monat = st.selectbox("Welchen Monat möchten Sie prognostizieren?", ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"])
    
    st.info("Das Modell sucht nun in den Daten von 1836 bis 2015 nach den statistisch besten Übereinstimmungen.")
    # (Die KI kann diesen Bereich später erweitern, sobald Ihr CSV-Format feststeht!)
