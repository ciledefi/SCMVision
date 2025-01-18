import schedule
import time
import streamlit as st
from backup_to_github import backup_to_github

def schedule_backup():
    # Plane die Backup-Funktion jeden Tag um 22:00 Uhr
    schedule.every().day.at("22:00").do(backup_to_github)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Starte den Scheduler in einem Thread
import threading
backup_thread = threading.Thread(target=schedule_backup, daemon=True)
backup_thread.start()

# Streamlit-Button für manuelle Backups
if st.button("Backup jetzt erstellen"):
    try:
        backup_to_github()
        st.success("Backup erfolgreich erstellt!")
    except Exception as e:
        st.error(f"Fehler beim Backup: {e}")