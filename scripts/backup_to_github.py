import os
import subprocess
from datetime import datetime

def configure_git():
    """
    Konfiguriert Git-Benutzerdaten für die Streamlit-Cloud-Umgebung.
    """
    subprocess.run(["git", "config", "--global", "user.name", "ciledefi"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "ciledefi@proton.me"], check=True)

def backup_to_github():
    """
    Funktion zum Sichern der Datenbank in ein GitHub-Repository.
    """
    # Git konfigurieren
    configure_git()

    # Repository-Root-Verzeichnis
    repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(repo_path)  # Ins Repository wechseln

    # Datenbank-Pfad
    db_path = os.path.join(repo_path, "pnl_data.db")

    # Überprüfen, ob die Datenbank existiert
    if not os.path.exists(db_path):
        print(f"Fehler: Datenbank {db_path} nicht gefunden.")
        return

    # Backup-Dateiname mit Zeitstempel
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"pnl_data_backup_{timestamp}.db"
    backup_path = os.path.join(repo_path, backup_filename)

    # Backup erstellen
    try:
        os.system(f"cp {db_path} {backup_path}")
        print(f"Backup erfolgreich erstellt: {backup_path}")

        # Git-Befehle ausführen
        subprocess.run(["git", "add", backup_filename], check=True)
        subprocess.run(["git", "commit", "-m", f"Backup der Datenbank am {timestamp}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Datenbank erfolgreich gesichert und hochgeladen.")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Sichern der Datenbank: {e}")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
