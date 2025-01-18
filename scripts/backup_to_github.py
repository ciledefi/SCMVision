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

    # GitHub PAT aus den Secrets abrufen
    github_pat = os.getenv("GITHUB_PAT")
    if not github_pat:
        raise ValueError("GitHub PAT fehlt in den Secrets!")

    # Git-Remote mit PAT konfigurieren
    repo_url = f"https://{github_pat}@github.com/ciledefi/SCMVision.git"
    subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=True)

    # Backup erstellen und hochladen
    db_path = "pnl_data.db"
    repo_path = "/app"
    os.chdir(repo_path)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"pnl_data_backup_{timestamp}.db"
    backup_path = os.path.join(repo_path, backup_filename)

    try:
        # Backup erstellen
        os.system(f"cp {db_path} {backup_path}")
        subprocess.run(["git", "add", backup_filename], check=True)
        subprocess.run(["git", "commit", "-m", f"Backup der Datenbank am {timestamp}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Datenbank erfolgreich gesichert und hochgeladen.")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Sichern der Datenbank: {e}")