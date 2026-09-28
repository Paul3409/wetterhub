# Mühlberg/Elbe — Eigenes Ensemble

GFS + AIFS Member-Pairing. T2m. 360 h. ~50 Linien.

## Nutzung

1. App öffnen
2. Links in der Sidebar auf **"Ensemble jetzt erzeugen"** klicken
3. Warten (~10–20 Sekunden)
4. Spaghetti-Plot erscheint
5. PNG-Download über:
   - Button rechts neben dem Plot **⬇️ PNG**
   - oder Kamera-Symbol oben rechts im Plot (Modebar)

## Farben
- Rot = gepaarte Member
- Grün = AIFS Extras
- Weiß (dick) = Mittelwert aller 50

## Hinweis
Daten werden im Streamlit-Container zwischengespeichert.
Nach Neustart der App muss neu erzeugt werden.

## Dateien
- `app.py` — komplette App (Fetch, Verarbeitung, Plot)
- `requirements.txt` — Python-Pakete
- `packages.txt` — System-Pakete (Chromium für Kaleido)
