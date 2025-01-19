import sqlite3

# Pfad zur Datenbank
db_path = "pnl_data.db"  # Ändern Sie diesen Pfad entsprechend, falls erforderlich

# Verbindung zur Datenbank herstellen
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Tabelleninhalt abfragen
cursor.execute("SELECT * FROM pnl_data")

# Ergebnisse ausgeben
rows = cursor.fetchall()
for row in rows:
    print(row)

# Verbindung schließen
conn.close()