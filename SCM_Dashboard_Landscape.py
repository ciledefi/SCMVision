import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json

# Funktion zum Laden von JSON-Daten
def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

# JSON-Dateien laden
kucoin_data = load_json("/Users/ciledefi/Library/Mobile Documents/com~apple~CloudDocs/SCM Vision/Controlling/Output/kucoin_pnl.json")
bitget_data = load_json("/Users/ciledefi/Library/Mobile Documents/com~apple~CloudDocs/SCM Vision/Controlling/Output/bitget_pnl.json")

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

# Funktion zum Erstellen von Gauges mit Pfeilen
def create_gauge(value, min_val, max_val, threshold_1, threshold_2):
    gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': f'PnL (%)'},
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

# Layout für Streamlit Dashboard
st.set_page_config(layout="wide")  # Setzt das Layout auf "wide", um den gesamten horizontalen Raum zu nutzen

# Zentraler Header
st.markdown("<h1 style='text-align: center;'>SCM Performance Dashboard</h1>", unsafe_allow_html=True)

# Aktuelle PnL Werte Tabelle
st.subheader("Aktuelle PnL Werte:")
st.dataframe(df, use_container_width=True)  # Tabelle über gesamte Breite anzeigen

# Performance Gauge - KuCoin, Bitget, Gesamt
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

plt.figure(figsize=(15, 5))  # Breite angepasst
plt.plot(dates, pnl_values, marker='o', label='Actual PnL', color='orange')
plt.title("PnL Verlauf über Wochen")
plt.xlabel("Datum")
plt.ylabel("Wert in USDT")
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(plt)

# Balkendiagramme als Platzhalter
st.subheader("Balkendiagramme (Platzhalter)")
col4, col5 = st.columns(2)

with col4:
    st.bar_chart([1, 2, 3, 4, 5])  # Platzhalter
    st.write("Kritische Trades")

with col5:
    st.bar_chart([10000, 15000, 20000])  # Platzhalter
    st.write("Aktives Kapital pro Börse")

# Hinweis zu weiteren Anpassungen
st.markdown("Die Balkendiagramme sind noch Platzhalter und können in späteren Versionen angepasst werden.")