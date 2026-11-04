
import subprocess
import time
from datetime import datetime

START_TIME = "11:10"
STOP_TIME = "11:11"

started_today = None
stopped_today = None

print("Notepad automation is running...")

while True:
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today = now.date()

    # Start Notepad
    if current_time == START_TIME and started_today != today:
        subprocess.Popen(["notepad.exe"])
        started_today = today
        print("Notepad started:", now)

    # Stop Notepad
    if current_time == STOP_TIME and stopped_today != today:
        subprocess.run(
            ["taskkill", "/IM", "notepad.exe", "/F"],
            capture_output=True
        )
        stopped_today = today
        print("Notepad stopped:", now)

    time.sleep(1)
