import streamlit as st
import os
import json
from debug_pnl import generate_pnl_data, get_root_output_dir

def load_json(filename):
    """
    Lädt eine JSON-Datei aus dem 'output'-Verzeichnis im Root.
    """
    output_dir = get_root_output_dir()
    filepath = os.path.join(output_dir, filename)

    try:
        with open(filepath, "r") as f:
            st.info(f"Lade Datei: {filepath}")  # Debugging
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Datei nicht gefunden: {filepath}")
        return {}

# Layout für Streamlit Dashboard
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>SCM Performance Dashboard</h1>", unsafe_allow_html=True)

# Button für JSON-Daten generieren
if st.sidebar.button("PnL-Daten generieren"):
    st.info("PnL-Daten werden generiert...")
    generate_pnl_data()
    st.success("PnL-Daten erfolgreich generiert!")

# JSON-Dateien laden
kucoin_data = load_json("kucoin_pnl.json")
bitget_data = load_json("bitget_pnl.json")

# Prüfen, ob Daten vorhanden sind
if kucoin_data and bitget_data:
    st.write("PnL-Daten erfolgreich geladen.")
    st.json(kucoin_data)
    st.json(bitget_data)
else:
    st.warning("Keine PnL-Daten verfügbar. Bitte generieren Sie die Daten zuerst.")