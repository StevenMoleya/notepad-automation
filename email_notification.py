
import os
import smtplib
import mimetypes
from pathlib import Path
from email.message import EmailMessage
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")


def send_notification(subject, message, log_file=None, attachments=None):
    try:
        # Validate credentials
        if not all([
            GMAIL_ADDRESS,
            GMAIL_APP_PASSWORD,
            NOTIFICATION_EMAIL
        ]):
            raise ValueError("Missing Gmail settings in .env file.")

        email = EmailMessage()
        email["From"] = GMAIL_ADDRESS
        email["To"] = NOTIFICATION_EMAIL
        email["Subject"] = subject
        email.set_content(message)

        # Collect attachments
        files_to_attach = []

        if log_file:
            files_to_attach.append(log_file)

        if attachments:
            files_to_attach.extend(attachments)

        # Attach files
        for file_path in files_to_attach:
            path = Path(file_path)

            if not path.is_file():
                raise FileNotFoundError(
                    f"Attachment not found: {path}"
                )

            mime_type, encoding = mimetypes.guess_type(path.name)

            if mime_type is None or encoding is not None:
                mime_type = "application/octet-stream"

            maintype, subtype = mime_type.split("/", 1)

            email.add_attachment(
                path.read_bytes(),
                maintype=maintype,
                subtype=subtype,
                filename=path.name
            )

        # Send email
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            smtp.send_message(email)

        print(f"Email sent successfully: {subject}")
        return True

    except Exception as error:
        print(f"Email failed: {error}")
        return False
