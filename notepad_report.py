
import os
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path

import psutil
import win32gui
import win32process
import win32con
from dotenv import load_dotenv

from email_notification import send_notification


# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

START_TIME = os.getenv("START_TIME", "08:10")
STOP_TIME = os.getenv("STOP_TIME", "08:13")


# Project files
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
notepad_process = None
notepad_window_handle = None

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


def get_notepad_window_handles():
    handles = []

    def callback(hwnd, extra):
        if not win32gui.IsWindowVisible(hwnd):
            return True

        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        try:
            if psutil.Process(pid).name().lower() == "notepad.exe":
                handles.append(hwnd)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        return True

    win32gui.EnumWindows(callback, None)

    return handles


def start_notepad():
    global session_start, session_timer
    global process_info, notepad_process, notepad_window_handle

    try:
        record_event("START_REQUESTED", "Opening Notepad")

        # Record existing windows before launching
        existing_windows = set(get_notepad_window_handles())

        notepad_process = subprocess.Popen(["notepad.exe"])

        # Wait for the new window to appear
        notepad_window_handle = None

        for _ in range(20):
            time.sleep(0.5)

            current_windows = set(get_notepad_window_handles())
            new_windows = current_windows - existing_windows

            if new_windows:
                notepad_window_handle = new_windows.pop()
                break

        if notepad_window_handle is None:
            raise RuntimeError(
                "Could not identify the new Notepad window."
            )

        process_info = get_notepad_processes()

        session_start = datetime.now()
        session_timer = time.monotonic()

        record_event(
            "NOTEPAD_STARTED",
            f"Window handle: {notepad_window_handle}"
        )

        message = (
            "Notepad automation started successfully.\n\n"
            f"Start time: {session_start}\n"
            f"Window handle: {notepad_window_handle}"
        )

        send_notification("Notepad Started", message)

    except Exception as error:
        record_event("START_ERROR", str(error))
        send_notification("Notepad Start Failed", str(error))


def stop_notepad():
    global process_info, notepad_process, notepad_window_handle

    stop_time = datetime.now()

    record_event("STOP_REQUESTED", "Closing automation Notepad")

    # Capture process information before closing
    processes_before_stop = get_notepad_processes()

    # Calculate session duration
    if session_timer is not None:
        duration = time.monotonic() - session_timer
        minutes, seconds = divmod(int(duration), 60)
        duration_text = f"{minutes} minutes and {seconds} seconds"
    else:
        duration_text = "Unknown"

    # Close only the identified Notepad window
    try:
        if (
            notepad_window_handle is not None
            and win32gui.IsWindow(notepad_window_handle)
        ):
            win32gui.PostMessage(
                notepad_window_handle,
                win32con.WM_CLOSE,
                0,
                0
            )

            stop_status = (
                f"Notepad window {notepad_window_handle} "
                "received a close request"
            )

        else:
            stop_status = (
                "Automation Notepad window was already closed"
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
        process_details = (
            "\nNo Notepad processes were detected before closing."
        )

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
    try:
        REPORT_FILE.write_text(report, encoding="utf-8")
        record_event("REPORT_GENERATED", str(REPORT_FILE))

    except OSError as error:
        record_event("REPORT_ERROR", str(error))
        return

    # Send closing email with attachments
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
