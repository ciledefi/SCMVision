import schedule
import time
from backup_to_github import backup_to_github

# Direkt beim Start ein Backup ausführen
try:
    backup_to_github()
    print("Initiales Backup erfolgreich erstellt!")
except Exception as e:
    print(f"Fehler beim initialen Backup: {e}")

# Plane tägliches Backup um 22:00 Uhr
def schedule_backup():
    schedule.every().day.at("22:00").do(backup_to_github)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Scheduler starten
import threading
backup_thread = threading.Thread(target=schedule_backup, daemon=True)
backup_thread.start()
