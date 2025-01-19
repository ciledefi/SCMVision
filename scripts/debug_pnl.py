import os
import json

def get_root_output_dir():
    """
    Gibt den absoluten Pfad zum 'output'-Verzeichnis im Root zurück.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)  # Verzeichnis erstellen, falls nicht vorhanden
    return output_dir

def save_pnl_to_json(exchange, investment, spot_balance, futures_balance, filename):
    """
    Speichert PnL-Daten im 'output'-Ordner des Root-Verzeichnisses.
    """
    total_balance = spot_balance + futures_balance
    pnl_percentage = ((total_balance - investment) / investment) * 100

    data = {
        "exchange": exchange,
        "investment": investment,
        "spot_balance": spot_balance,
        "futures_balance": futures_balance,
        "total_balance": total_balance,
        "pnl_percentage": pnl_percentage,
    }

    output_dir = get_root_output_dir()
    filepath = os.path.join(output_dir, filename)
    print(f"Speichere Datei in: {filepath}")

    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

    print(f"PnL-Daten für {exchange} erfolgreich in {filepath} gespeichert.")

def generate_pnl_data():
    """
    Generiert Dummy-PnL-Daten für Debugging.
    """
    save_pnl_to_json("KuCoin", 1000, 500, 600, "kucoin_pnl.json")
    save_pnl_to_json("Bitget", 1200, 800, 400, "bitget_pnl.json")
    print("PnL-Daten wurden erfolgreich gespeichert.")