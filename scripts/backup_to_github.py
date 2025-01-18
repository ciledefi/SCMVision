import os
import subprocess
from datetime import datetime

def configure_git_with_pat():
    """
    Konfiguriert Git mit den Benutzerdaten und setzt den Remote-URL mit PAT.
    """
    # Setze Benutzername und E-Mail
    subprocess.run(["git", "config", "--global", "user.name", "ciledefi"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "ciledefi@proton.me"], check=True)

    # Setze den Remote-URL mit PAT
    pat = os.getenv("GITHUB_PAT")  # PAT aus den Streamlit-Secrets oder Umgebungsvariablen
    if not pat:
        raise EnvironmentError("GITHUB_PAT ist nicht in den Secrets oder Umgebungsvariablen definiert.")
    
    repo_url = f"https://ciledefi:{pat}@github.com/ciledefi/SCMVision.git"
    subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=True)

def backup_to_github():
    """
    Führt ein Backup der SQLite-Datenbank durch und pusht die Änderungen auf GitHub.
    """
    # Git konfigurieren
    configure_git_with_pat()

    # Pfade definieren
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Ordner, in dem das Skript liegt
    repo_path = os.path.abspath(os.path.join(script_dir, ".."))  # Root der Repository
    db_path = os.path.join(repo_path, "pnl_data.db")  # Absoluter Pfad zur Datenbank

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