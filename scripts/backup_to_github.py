import os
from datetime import datetime
import subprocess

def backup_to_github():
    # Repository-Root-Verzeichnis
    repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(repo_path)  # Wechsle ins Repository-Verzeichnis

    # Absoluter Pfad zur Datenbank
    db_path = os.path.join(repo_path, "pnl_data.db")

    # Überprüfe, ob die Datenbank existiert
    if not os.path.exists(db_path):
        print(f"Fehler: Datenbankdatei {db_path} wurde nicht gefunden.")
        return

    # Backup-Dateiname mit Zeitstempel
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"pnl_data_backup_{timestamp}.db"
    backup_path = os.path.join(repo_path, backup_filename)

    # Backup erstellen
    os.system(f"cp {db_path} {backup_path}")
    print(f"Backup erfolgreich erstellt: {backup_path}")

    # Git-Befehle ausführen
    try:
        subprocess.run(["git", "add", backup_filename], check=True)
        subprocess.run(["git", "commit", "-m", f"Backup der Datenbank am {timestamp}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Datenbank erfolgreich gesichert und hochgeladen.")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Hochladen zu GitHub: {e}")