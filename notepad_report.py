import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path

import psutil
from email_notification import send_notification


import os
from dotenv import load_dotenv

load_dotenv()

START_TIME = os.getenv("START_TIME", "08:10")
STOP_TIME = os.getenv("STOP_TIME", "08:13")


# Project files
BASE_DIR = Path(__file__).resolve().parent

LOG_FILE = BASE_DIR / "notepad_automation.log"
REPORT_FILE = BASE_DIR / "notepad_report.txt"


# Logging configuration
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# Session information
session_start = None
session_timer = None
process_info = []

started_today = None
stopped_today = None


def record_event(action, details=""):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = f"{timestamp} | {action} | {details}"

    logging.info("%s | %s", action, details)

    print(entry)


def get_notepad_processes():

    processes = []

    for process in psutil.process_iter(
        ["pid", "name", "exe", "create_time"]
    ):

        try:
            if (process.info["name"] or "").lower() == "notepad.exe":

                processes.append({
                    "PID": process.info["pid"],
                    "Executable": process.info["exe"] or "Unknown",
                    "Created": datetime.fromtimestamp(
                        process.info["create_time"]
                    ).strftime("%Y-%m-%d %H:%M:%S")
                })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes


def start_notepad():

    global session_start, session_timer, process_info

    try:

        record_event("START_REQUESTED", "Opening Notepad")

        subprocess.Popen(["notepad.exe"])

        time.sleep(2)

        process_info = get_notepad_processes()

        session_start = datetime.now()
        session_timer = time.monotonic()

        record_event(
            "NOTEPAD_STARTED",
            f"Processes detected: {len(process_info)}"
        )

        message = (
            "Notepad automation started successfully.\n\n"
            f"Start time: {session_start}\n"
            f"Processes detected: {len(process_info)}"
        )

        for process in process_info:
            message += (
                f"\nPID: {process['PID']}"
                f"\nExecutable: {process['Executable']}"
            )

        send_notification("Notepad Started", message)

    except Exception as error:

        record_event("START_ERROR", str(error))

        send_notification(
            "Notepad Start Failed",
            str(error)
        )


def stop_notepad():

    global process_info

    stop_time = datetime.now()

    record_event("STOP_REQUESTED", "Closing Notepad")

    # Capture processes before closing
    processes_before_stop = get_notepad_processes()

    # Calculate session duration
    if session_timer is not None:

        duration = time.monotonic() - session_timer

        minutes, seconds = divmod(int(duration), 60)

        duration_text = f"{minutes} minutes and {seconds} seconds"

    else:
        duration_text = "Unknown"

    # Close Notepad processes
    try:

        result = subprocess.run(
            ["taskkill", "/IM", "notepad.exe", "/F"],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode == 0:
            stop_status = "Notepad processes terminated successfully"
        else:
            stop_status = (
                result.stderr.strip()
                or result.stdout.strip()
                or "No Notepad process was terminated"
            )

    except Exception as error:

        stop_status = f"Closing error: {error}"

    record_event("NOTEPAD_STOPPED", stop_status)

    # Build process information
    process_details = ""

    for process in processes_before_stop:

        process_details += (
            f"\nPID: {process['PID']}"
            f"\nExecutable: {process['Executable']}"
            f"\nCreated: {process['Created']}\n"
        )

    if not process_details:
        process_details = "\nNo Notepad processes were detected before closing."

    # Build activity report
    report = f"""
NOTEPAD SESSION ACTIVITY REPORT
================================

SESSION DETAILS
---------------

Start time: {session_start or 'Unknown'}
Stop time: {stop_time}
Duration: {duration_text}

PROCESS INFORMATION
-------------------

{process_details}

STOP RESULT
-----------

{stop_status}

AUTOMATION ACTIVITY
-------------------

See the attached notepad_automation.log file for
the recorded sequence of automation events.

REPORT GENERATED
----------------

{datetime.now()}
"""

    # Save report
    REPORT_FILE.write_text(report, encoding="utf-8")

    record_event("REPORT_GENERATED", str(REPORT_FILE))

    # Send closing email with both attachments
    email_sent = send_notification(
        "Notepad Closed - Session Activity Report",
        (
            "Notepad automation has completed.\n\n"
            f"Session duration: {duration_text}\n"
            f"Stop result: {stop_status}\n\n"
            "Attached are the session report and automation log."
        ),
        attachments=[
            str(REPORT_FILE),
            str(LOG_FILE)
        ]
    )

    record_event("CLOSING_EMAIL_RESULT", str(email_sent))


# Main automation loop
print("Notepad monitoring automation running...")
print(f"Scheduled start: {START_TIME}")
print(f"Scheduled stop: {STOP_TIME}")

record_event("AUTOMATION_STARTED", "Monitoring schedule")


while True:

    now = datetime.now()

    current_time = now.strftime("%H:%M")
    today = now.date()

    if current_time == START_TIME and started_today != today:

        start_notepad()
        started_today = today

    if current_time == STOP_TIME and stopped_today != today:

        stop_notepad()
        stopped_today = today

    time.sleep(1)
