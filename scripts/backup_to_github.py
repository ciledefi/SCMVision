import os
from datetime import datetime
import subprocess

def backup_to_github():
    """
    Funktion zum Sichern der Datenbank in ein GitHub-Repository.
    """
    # Verzeichnispfade
    repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # Root-Verzeichnis
    db_path = os.path.join(repo_path, "pnl_data.db")  # Absoluter Pfad zur Datenbank

    # Prüfe, ob die Datenbank existiert
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Datenbank nicht gefunden: {db_path}")

    # Zum Git-Repository wechseln
    os.chdir(repo_path)

    # Backup-Dateiname mit Zeitstempel
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"pnl_data_backup_{timestamp}.db"
    backup_path = os.path.join(repo_path, backup_filename)

    # Datenbank kopieren
    os.system(f"cp {db_path} {backup_path}")

    # Git-Befehle ausführen
    try:
        subprocess.run(["git", "add", backup_filename], check=True)
        subprocess.run(["git", "commit", "-m", f"Backup der Datenbank am {timestamp}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Datenbank erfolgreich gesichert und hochgeladen.")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Sichern der Datenbank: {e}")