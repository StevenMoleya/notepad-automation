import os
import smtplib
from pathlib import Path
from email.message import EmailMessage
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")


def send_notification(subject, message, log_file=None, attachments=None):

    email = EmailMessage()
    email["From"] = GMAIL_ADDRESS
    email["To"] = NOTIFICATION_EMAIL
    email["Subject"] = subject
    email.set_content(message)

    files_to_attach = []

    if log_file:
        files_to_attach.append(log_file)

    if attachments:
        files_to_attach.extend(attachments)

    for file_path in files_to_attach:
        path = Path(file_path)

        if path.exists():
            email.add_attachment(
                path.read_bytes(),
                maintype="text",
                subtype="plain",
                filename=path.name
            )

    try:
        if not all([GMAIL_ADDRESS, GMAIL_APP_PASSWORD, NOTIFICATION_EMAIL]):
            raise ValueError("Missing Gmail settings in .env file.")

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            smtp.send_message(email)

        print(f"Email sent successfully: {subject}")
        return True

    except Exception as error:
        print(f"Email failed: {error}")
        return False
