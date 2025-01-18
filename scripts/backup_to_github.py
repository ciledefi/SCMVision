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

    # Pfade definieren
    db_path = "pnl_data.db"
    repo_path = "/app"
    os.chdir(repo_path)

    # Backup-Dateiname mit Zeitstempel
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"pnl_data_backup_{timestamp}.db"
    backup_path = os.path.join(repo_path, backup_filename)

    # Datenbank sichern
    try:
        os.system(f"cp {db_path} {backup_path}")
        subprocess.run(["git", "add", backup_filename], check=True)
        subprocess.run(["git", "commit", "-m", f"Backup der Datenbank am {timestamp}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Datenbank erfolgreich gesichert und hochgeladen.")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Sichern der Datenbank: {e}")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
