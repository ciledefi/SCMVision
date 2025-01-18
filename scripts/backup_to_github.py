import subprocess
import os
from datetime import datetime

def backup_to_github():
    """
    Funktion zum Sichern der Datenbank in ein GitHub-Repository.
    """
    # Pfade definieren
    db_path = "pnl_data.db"  # Pfad zur Datenbank
    repo_path = "/app"  # Pfad zum GitHub-Repository auf Streamlit Cloud
    os.chdir(repo_path)  # Zum Repository wechseln

    # Backup-Dateiname mit Zeitstempel
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"pnl_data_backup_{timestamp}.db"
    os.system(f"cp {db_path} {repo_path}/{backup_filename}")

    # Git-Befehle ausführen
    try:
        subprocess.run(["git", "add", backup_filename], check=True)
        subprocess.run(["git", "commit", "-m", f"Backup der Datenbank am {timestamp}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Datenbank erfolgreich gesichert und hochgeladen.")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Sichern der Datenbank: {e}")