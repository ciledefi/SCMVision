import requests
import hmac
import hashlib
import base64
import time
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API-Konfigurationen
api_key_bitget = os.getenv("API_KEY_BITGET")
api_secret_bitget = os.getenv("API_SECRET_BITGET")
api_passphrase_bitget = os.getenv("API_PASSPHRASE_BITGET")

api_key_kucoin = os.getenv("API_KEY_KUCOIN")
api_secret_kucoin = os.getenv("API_SECRET_KUCOIN")
api_passphrase_kucoin = os.getenv("API_PASSPHRASE_KUCOIN")


def get_root_output_dir():
    """
    Gibt den absoluten Pfad zum 'output'-Verzeichnis im Root zurück.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)  # Verzeichnis erstellen, falls nicht vorhanden
    return output_dir


# Header-Erstellung für KuCoin
def create_kucoin_headers(api_secret, api_passphrase, method, request_path, body=""):
    now = str(int(time.time() * 1000))
    str_to_sign = now + method + request_path + body
    signature = base64.b64encode(
        hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest()
    )
    passphrase = base64.b64encode(
        hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest()
    )
    return {
        "KC-API-KEY": api_key_kucoin,
        "KC-API-SIGN": signature.decode(),
        "KC-API-TIMESTAMP": now,
        "KC-API-PASSPHRASE": passphrase.decode(),
        "KC-API-KEY-VERSION": "2",
    }

# Header-Erstellung für Bitget
def create_bitget_headers(api_key, api_secret, api_passphrase, method, request_path, query_string=""):
    timestamp = str(int(time.time() * 1000))
    string_to_sign = f"{timestamp}{method}{request_path}{query_string}"
    sign = base64.b64encode(hmac.new(api_secret.encode(), string_to_sign.encode(), hashlib.sha256).digest())
    return {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": sign.decode(),
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": api_passphrase,
        "ACCESS-KEY-VERSION": "2",
        "Content-Type": "application/json",
    }

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

# Funktion: Preise von KuCoin abrufen
def get_prices_kucoin():
    url = "https://api.kucoin.com/api/v1/prices"
    response = requests.get(url)
    prices = {"USDT": 1.0}  # USDT manuell auf 1.0 setzen

    if response.status_code == 200:
        prices_data = response.json()["data"]
        for symbol, price in prices_data.items():
            prices[symbol] = float(price)
        return prices
    else:
        print("Fehler beim Abrufen der Preise:", response.status_code, response.text)
        return {}

# Preise von Bitget abrufen
def get_prices_bitget():
    url = "https://api.bitget.com/api/spot/v1/market/tickers"
    response = requests.get(url)
    prices = {"USDT": 1.0}  # USDT manuell auf 1.0 setzen

    if response.status_code == 200:
        data = response.json().get("data", [])
        for item in data:
            if "USDT" in item["symbol"]:
                symbol = item["symbol"].replace("USDT", "")
                prices[symbol] = float(item["close"])
        return prices
    else:
        print("Fehler beim Abrufen der Preise:", response.status_code, response.text)
        return {}


# Funktion zum Abrufen des Spot-Guthabens von KuCoin
def get_spot_balance_kucoin(prices):
    url = "https://api.kucoin.com/api/v1/accounts"
    headers = create_kucoin_headers(api_secret_kucoin, api_passphrase_kucoin, "GET", "/api/v1/accounts")
    response = requests.get(url, headers=headers)
    total_spot_balance = 0.0

    if response.status_code == 200:
        data = response.json()["data"]
        for asset in data:
            currency = asset["currency"]
            balance = float(asset["balance"])
            price_in_usdt = prices.get(currency, 0)
            total_spot_balance += balance * price_in_usdt
    else:
        print("Fehler beim Abrufen der Spot-Daten von KuCoin:", response.status_code, response.text)
    return total_spot_balance

# Funktion zum Abrufen des Spot-Guthabens von Bitget
def get_spot_balance_bitget(prices):
    url = "https://api.bitget.com/api/spot/v1/account/assets"
    headers = create_bitget_headers(api_key_bitget, api_secret_bitget, api_passphrase_bitget, "GET", "/api/spot/v1/account/assets")
    response = requests.get(url, headers=headers)
    total_spot_balance = 0.0

    if response.status_code == 200:
        data = response.json().get("data", [])
        for asset in data:
            coin = asset.get("coinName")
            total_amount = float(asset.get("available", 0)) + float(asset.get("frozen", 0))
            total_spot_balance += total_amount * prices.get(coin, 0)
    else:
        print("Fehler beim Abrufen der Spot-Daten von Bitget:", response.status_code, response.text)
    return total_spot_balance


# Funktion zum Abrufen des Futures-Guthabens von KuCoin
def get_futures_balance_kucoin():
    url = "https://api-futures.kucoin.com/api/v1/account-overview?currency=USDT"
    headers = create_kucoin_headers(api_secret_kucoin, api_passphrase_kucoin, "GET", "/api/v1/account-overview?currency=USDT")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return float(response.json()["data"].get("availableBalance", 0))
    else:
        print("Fehler beim Abrufen der Futures-Daten von KuCoin:", response.status_code, response.text)
        return 0.0
    
    # Funktion zum Abrufen des Futures-Guthabens von Bitget
def get_futures_balance_bitget():
    url = "https://api.bitget.com/api/mix/v1/account/accounts"
    query_string = "?productType=umcbl"
    headers = create_bitget_headers(api_key_bitget, api_secret_bitget, api_passphrase_bitget, "GET", "/api/mix/v1/account/accounts", query_string)
    response = requests.get(url + query_string, headers=headers)
    total_futures_balance = 0.0
    
    if response.status_code == 200:
        data = response.json().get("data", [])
        for asset in data:
            total_futures_balance += float(asset.get("usdtEquity", 0))
    else:
        print("Fehler beim Abrufen der Futures-Daten von Bitget:", response.status_code, response.text)
    return total_futures_balance


# Hauptlogik
def generate_pnl_data():
    investments = {
        "KuCoin": float(os.getenv("INVESTMENT_KUCOIN", 0)),
        "Bitget": float(os.getenv("INVESTMENT_BITGET", 0)),
    }

    prices_kucoin = get_prices_kucoin()
    prices_bitget = get_prices_bitget()

    total_spot_balance_kucoin = get_spot_balance_kucoin(prices_kucoin)
    total_spot_balance_bitget = get_spot_balance_bitget(prices_bitget)

    total_futures_balance_kucoin = get_futures_balance_kucoin()
    total_futures_balance_bitget = get_futures_balance_bitget()

    save_pnl_to_json("KuCoin", investments["KuCoin"], total_spot_balance_kucoin, total_futures_balance_kucoin, "kucoin_pnl.json")
    save_pnl_to_json("Bitget", investments["Bitget"], total_spot_balance_bitget, total_futures_balance_bitget, "bitget_pnl.json")
    print("PnL-Daten wurden erfolgreich gespeichert.")

if __name__ == "__main__":
    generate_pnl_data()