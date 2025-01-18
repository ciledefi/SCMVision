import os
from datetime import datetime
import subprocess

def backup_to_github():
    """
    Funktion zum Sichern der Datenbank in ein GitHub-Repository.
    """
    # Pfade definieren
    db_path = "../pnl_data.db"  # Relativer Pfad zur Datenbank
    repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(repo_path)  # Zum Repository wechseln

    # Backup-Dateiname mit Zeitstempel
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"pnl_data_backup_{timestamp}.db"
    backup_path = os.path.join(repo_path, backup_filename)

    # Überprüfen, ob die Datenbank existiert
    if not os.path.exists(db_path):
        print(f"Fehler: Datenbankdatei {db_path} wurde nicht gefunden.")
        return

    # Kopiere die Datei
    try:
        os.system(f"cp {db_path} {backup_path}")
        print(f"Backup erfolgreich erstellt: {backup_path}")
    except Exception as e:
        print(f"Fehler beim Erstellen des Backups: {e}")
        return

    # Git-Befehle ausführen
    try:
        subprocess.run(["git", "add", backup_filename], check=True)
        subprocess.run(["git", "commit", "-m", f"Backup der Datenbank am {timestamp}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Datenbank erfolgreich gesichert und hochgeladen.")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Hochladen zu GitHub: {e}")