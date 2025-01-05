import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os
from SCM_PnL_Output_JSON_full_refactored_streamlit import generate_pnl_data, get_root_output_dir  # Importiere die PnL-Funktion


# Globale Variable für den Output-Ordner
output_dir = get_root_output_dir()

def load_json(filename):
    """
    Lädt eine JSON-Datei aus dem 'output'-Verzeichnis im Root.
    """
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

# JSON-Daten generieren (Button)
if st.sidebar.button("PnL-Daten generieren"):
    st.info("PnL-Daten werden generiert...")
    print("Generierungs-Button wurde geklickt")  # Debug-Ausgabe
    generate_pnl_data()
    st.success("PnL-Daten erfolgreich generiert!")
    st.write(f"Dateien wurden im Output-Ordner ({output_dir}) gespeichert.")

# JSON-Dateien laden
kucoin_data = load_json("kucoin_pnl.json")
bitget_data = load_json("bitget_pnl.json")

# Prüfen, ob Daten vorhanden sind
if kucoin_data and bitget_data:
    # Gesamtdaten berechnen
    total_spot = kucoin_data["spot_balance"] + bitget_data["spot_balance"]
    total_futures = kucoin_data["futures_balance"] + bitget_data["futures_balance"]
    total_invest = kucoin_data["investment"] + bitget_data["investment"]
    total_actual = kucoin_data["total_balance"] + bitget_data["total_balance"]
    total_abs_pnl = total_actual - total_invest
    total_rel_pnl = (total_abs_pnl / total_invest) * 100

    # DataFrame aus JSON-Daten erstellen
    data = {
        "Börse": ["KuCoin", "Bitget", "Gesamt"],
        "Spot": [kucoin_data["spot_balance"], bitget_data["spot_balance"], total_spot],
        "Futures": [kucoin_data["futures_balance"], bitget_data["futures_balance"], total_futures],
        "Invest": [kucoin_data["investment"], bitget_data["investment"], total_invest],
        "Actual": [kucoin_data["total_balance"], bitget_data["total_balance"], total_actual],
        "Abs PnL": [
            kucoin_data["total_balance"] - kucoin_data["investment"],
            bitget_data["total_balance"] - bitget_data["investment"],
            total_abs_pnl,
        ],
        "Rel PnL": [
            ((kucoin_data["total_balance"] - kucoin_data["investment"]) / kucoin_data["investment"]) * 100,
            ((bitget_data["total_balance"] - bitget_data["investment"]) / bitget_data["investment"]) * 100,
            total_rel_pnl,
        ],
    }
    df = pd.DataFrame(data)

    # Funktion zum Erstellen von Gauges
    def create_gauge(value, min_val, max_val, threshold_1, threshold_2):
        gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            title={'text': 'PnL (%)'},
            delta={'reference': 0},
            gauge={
                'axis': {'range': [min_val, max_val]},
                'bar': {'color': "green"},
                'steps': [
                    {'range': [min_val, threshold_1], 'color': "red"},
                    {'range': [threshold_1, threshold_2], 'color': "yellow"},
                    {'range': [threshold_2, max_val], 'color': "green"},
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value,
                },
            },
        ))
        return gauge

    # Aktuelle PnL Werte Tabelle
    st.subheader("Aktuelle PnL Werte:")
    st.dataframe(df, use_container_width=True)

    # Performance Gauges
    st.subheader("Performance/Profit")
    col1, col2, col3 = st.columns(3)

    with col1:
        gauge_kucoin = create_gauge(df.loc[0, 'Rel PnL'], -25, 25, 2, 15)
        st.write("KuCoin Performance:")
        st.plotly_chart(gauge_kucoin, use_container_width=True)

    with col2:
        gauge_bitget = create_gauge(df.loc[1, 'Rel PnL'], -25, 25, 2, 15)
        st.write("Bitget Performance:")
        st.plotly_chart(gauge_bitget, use_container_width=True)

    with col3:
        gauge_total = create_gauge(df.loc[2, 'Rel PnL'], -25, 25, 2, 15)
        st.write("Gesamt Performance:")
        st.plotly_chart(gauge_total, use_container_width=True)

    # PnL Verlauf über Wochen (Dummy-Daten)
    st.subheader("PnL Verlauf über Wochen")
    dates = [datetime.today() - pd.DateOffset(weeks=i) for i in range(7)]
    pnl_values = [23500, 23600, 23450, 23700, 23650, 23750, 23800]

    plt.figure(figsize=(15, 5))
    plt.plot(dates, pnl_values, marker='o', label='Actual PnL', color='orange')
    plt.title("PnL Verlauf über Wochen")
    plt.xlabel("Datum")
    plt.ylabel("Wert in USDT")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)

else:
    st.warning("Keine PnL-Daten verfügbar. Bitte generieren Sie die Daten zuerst.")