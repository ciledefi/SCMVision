import sqlite3
import os

def setup_database():
    db_path = os.getenv("DB_PATH", "pnl_data.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabelle erstellen oder prüfen, ob sie existiert
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pnl_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            exchange TEXT NOT NULL,
            spot_balance REAL NOT NULL,
            futures_balance REAL NOT NULL,
            total_balance REAL NOT NULL,
            pnl_percentage REAL NOT NULL,
            UNIQUE(date, exchange)  -- UNIQUE-Constraint auf Datum und Börse
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Datenbank wurde unter {db_path} eingerichtet.")

def insert_or_update_pnl_data(date, exchange, spot_balance, futures_balance, total_balance, pnl_percentage):
    """
    Fügt PnL-Daten in die Datenbank ein oder aktualisiert bestehende Einträge.
    """
    db_path = os.getenv("DB_PATH", "pnl_data.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Einfügen oder Aktualisieren der PnL-Daten
    cursor.execute('''
        INSERT INTO pnl_data (date, exchange, spot_balance, futures_balance, total_balance, pnl_percentage)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(date, exchange)
        DO UPDATE SET
            spot_balance = excluded.spot_balance,
            futures_balance = excluded.futures_balance,
            total_balance = excluded.total_balance,
            pnl_percentage = excluded.pnl_percentage;
    ''', (date, exchange, spot_balance, futures_balance, total_balance, pnl_percentage))
    
    conn.commit()
    conn.close()
    print(f"PnL-Daten für {exchange} am {date} erfolgreich in die Datenbank eingefügt oder aktualisiert.")

if __name__ == "__main__":
    # Datenbank einrichten
    setup_database()