from SCM_PnL_Output_JSON_full_refactored_streamlit import generate_pnl_data

def daily_pnl_routine():
    try:
        # Generiere und speichere die PnL-Daten
        generate_pnl_data()
        print("Tägliche PnL-Daten wurden erfolgreich gespeichert.")
    except Exception as e:
        print(f"Fehler beim Speichern der PnL-Daten: {e}")

if __name__ == "__main__":
    daily_pnl_routine()