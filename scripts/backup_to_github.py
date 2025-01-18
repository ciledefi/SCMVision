import os
import subprocess
from datetime import datetime
import streamlit as st  # Nur für Streamlit-Umgebungen erforderlich

def configure_git_with_pat():
    """
    Konfiguriert die Git-Remote-URL mit dem in Streamlit-Secrets gespeicherten PAT.
    """
    pat = st.secrets.get("GITHUB_PAT", "")
    username = st.secrets.get("GITHUB_USERNAME", "")
    
    if not pat or not username:
        raise ValueError("GITHUB_PAT oder GITHUB_USERNAME fehlen in den Streamlit-Secrets.")
    
    repo_url = f"https://{username}:{pat}@github.com/{username}/SCMVision.git"
    subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=True)

def backup_to_github():
    """
    Führt ein Backup der SQLite-Datenbank durch und pusht die Änderungen auf GitHub.
    """
    # Git konfigurieren
    configure_git_with_pat()

    # Pfade definieren
    repo_path = "/app"  # Verzeichnis, in dem die App läuft
    db_path = os.path.join(repo_path, "pnl_data.db")
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Datenbank {db_path} wurde nicht gefunden.")
    
    os.chdir(repo_path)

    # Backup-Dateiname mit Zeitstempel
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"pnl_data_backup_{timestamp}.db"
    backup_path = os.path.join(repo_path, backup_filename)

    # Backup erstellen
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