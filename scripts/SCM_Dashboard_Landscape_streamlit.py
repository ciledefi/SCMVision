import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import os
from dotenv import load_dotenv
from SCM_PnL_Output_JSON_full_refactored_streamlit import generate_pnl_data, get_root_output_dir
from gauge_utils import create_gauge  # Importiere die ausgelagerte Funktion

import warnings

# Unterdrücke spezifische Warnungen
warnings.filterwarnings("ignore", message="missing ScriptRunContext! This warning can be ignored when running in bare mode")


# Layout für Streamlit Dashboard
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>SCM Performance Dashboard</h1>", unsafe_allow_html=True)

# Umgebungsvariablen laden
load_dotenv()
LOCAL_MODE = os.getenv("LOCAL_MODE", "true").lower() == "true"

# Funktion: Zugriff auf Investment-Werte
def get_investment(exchange):
    if LOCAL_MODE:
        key = f"INVESTMENT_{exchange.upper()}"
        return float(os.getenv(key, 0))
    else:
        key = f"investment.{exchange.lower()}"
        return float(st.secrets[key])

# Verbindung zur SQLite-Datenbank herstellen
def fetch_pnl_data():
    db_path = os.getenv("DB_PATH", "pnl_data.db")
    if not os.path.exists(db_path):
        print(f"Datenbank {db_path} wird erstellt...")
        # Erstellen der Datenbank hier
    else:
        print(f"Datenbank {db_path} existiert bereits.")
    conn = sqlite3.connect(db_path)
    query = """
    SELECT date, exchange, spot_balance, futures_balance, total_balance, pnl_percentage
    FROM pnl_data
    ORDER BY date ASC;
    """
    data = pd.read_sql_query(query, conn)
    conn.close()
    return data

# Zeitbereichsauswahl hinzufügen
zeitbereich = st.radio(
    "Wähle den Zeitraum für den PnL-Verlauf:",
    ("Monatlich", "Quartalsweise", "Jährlich"),
    index=0
)

# Daten entsprechend des Zeitbereichs anpassen
def get_time_filtered_data(data, zeitraum):
    if zeitraum == "Monatlich":
        start_date = pd.Timestamp.now() - pd.DateOffset(days=30)
        resample_freq = 'D'
    elif zeitraum == "Quartalsweise":
        start_date = pd.Timestamp.now() - pd.DateOffset(weeks=13)
        resample_freq = 'W'
    elif zeitraum == "Jährlich":
        start_date = pd.Timestamp.now() - pd.DateOffset(months=12)
        resample_freq = 'M'

    # Filter und Gruppierung
    filtered_data = data[data['date'] >= start_date]
    grouped_data = filtered_data.groupby(['exchange', pd.Grouper(key='date', freq=resample_freq)]).mean().reset_index()
    return grouped_data, resample_freq

# PnL-Daten generieren
try:
    generate_pnl_data()
    print("PnL-Daten erfolgreich generiert.")
except Exception as e:
    st.error(f"Fehler beim Generieren der PnL-Daten: {e}")


# Daten aus der Datenbank laden
pnl_data = fetch_pnl_data()

# Datumsspalte in datetime konvertieren
pnl_data['date'] = pd.to_datetime(pnl_data['date'], errors='coerce')

# Überprüfe, ob es ungültige Datumswerte gibt
if pnl_data['date'].isnull().any():
    print("Warnung: Ungültige Datumswerte in den Daten!")
    pnl_data = pnl_data.dropna(subset=['date'])

if not pnl_data.empty:
    # Letzte Einträge für jede Börse abrufen
    latest_data = pnl_data.groupby('exchange').last().reset_index()

    # Daten für die Tabelle sicherstellen
    kucoin_investment = get_investment("KuCoin")
    bitget_investment = get_investment("Bitget")
    total_investment = kucoin_investment + bitget_investment

    # Fehlende Einträge prüfen und auffüllen
    if 'KuCoin' not in latest_data['exchange'].values:
        latest_data = pd.concat(
            [latest_data, pd.DataFrame([{'exchange': 'KuCoin', 'spot_balance': 0, 'futures_balance': 0, 'total_balance': 0}])]
        )
    if 'Bitget' not in latest_data['exchange'].values:
        latest_data = pd.concat(
            [latest_data, pd.DataFrame([{'exchange': 'Bitget', 'spot_balance': 0, 'futures_balance': 0, 'total_balance': 0}])]
        )

    # Reihenfolge festlegen
    latest_data = latest_data.set_index('exchange').reindex(['KuCoin', 'Bitget']).reset_index()

    # Berechnung der Gesamtwerte
    total_spot = latest_data['spot_balance'].sum()
    total_futures = latest_data['futures_balance'].sum()
    total_actual = latest_data['total_balance'].sum()
    total_abs_pnl = total_actual - total_investment
    total_rel_pnl = (total_abs_pnl / total_investment) * 100

    # DataFrame für die Tabelle erstellen
    table_data = {
        "Börse": ["KuCoin", "Bitget", "Gesamt"],
        "Spot": latest_data['spot_balance'].tolist() + [total_spot],
        "Futures": latest_data['futures_balance'].tolist() + [total_futures],
        "Invest": [kucoin_investment, bitget_investment, total_investment],
        "Actual": latest_data['total_balance'].tolist() + [total_actual],
        "Abs PnL": [
            latest_data.loc[0, 'total_balance'] - kucoin_investment,
            latest_data.loc[1, 'total_balance'] - bitget_investment,
            total_abs_pnl,
        ],
        "Rel PnL": [
            ((latest_data.loc[0, 'total_balance'] - kucoin_investment) / kucoin_investment) * 100 if kucoin_investment > 0 else 0,
            ((latest_data.loc[1, 'total_balance'] - bitget_investment) / bitget_investment) * 100 if bitget_investment > 0 else 0,
            total_rel_pnl,
        ],
    }

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)

    # Farben für die Gauges
    colors = ["#7E57C2", "#9575CD", "#B39DDB", "#D3D3D3"]  # Lila-Töne + Grau

    # Gauges anzeigen
    st.subheader("Performance/Profit")
    col1, col2, col3 = st.columns(3)

    with col1:
        gauge_kucoin = create_gauge(df.loc[0, 'Rel PnL'], -25, 25, 2, 15, colors)
        st.write("KuCoin Performance:")
        st.plotly_chart(gauge_kucoin, use_container_width=True)

    with col2:
        gauge_bitget = create_gauge(df.loc[1, 'Rel PnL'], -25, 25, 2, 15, colors)
        st.write("Bitget Performance:")
        st.plotly_chart(gauge_bitget, use_container_width=True)

    with col3:
        gauge_total = create_gauge(df.loc[2, 'Rel PnL'], -25, 25, 2, 15, colors)
        st.write("Gesamt Performance:")
        st.plotly_chart(gauge_total, use_container_width=True)

    # Verlaufsgrafik erstellen
    filtered_data, freq = get_time_filtered_data(pnl_data, zeitbereich)

    st.subheader(f"PnL Verlauf ({zeitbereich})")
    fig = go.Figure()

    for exchange in ["KuCoin", "Bitget", "Gesamt"]:
        exchange_data = filtered_data[filtered_data['exchange'] == exchange]
        fig.add_trace(go.Scatter(
            x=exchange_data['date'],
            y=exchange_data['pnl_percentage'],
            mode='lines+markers',
            name=f"{exchange} PnL (%)"
        ))

    fig.update_layout(
        title="PnL Verlauf über den Zeitraum",
        xaxis_title="Datum",
        yaxis_title="PnL (%)",
        xaxis=dict(tickformat="%b %d" if freq == 'D' else "%b" if freq == 'M' else "%d.%m.%Y"),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Keine PnL-Daten verfügbar. Bitte generieren Sie die Daten zuerst.")

if st.sidebar.button("PnL-Daten generieren"):
    try:
        generate_pnl_data()
        st.success("PnL-Daten erfolgreich generiert!")
        st.session_state["reload"] = True  # Markiere die Seite zur Aktualisierung
    except Exception as e:
        st.error(f"Fehler beim Generieren der PnL-Daten: {e}")