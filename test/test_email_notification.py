
import smtplib

from email_notification import send_notification


def test_send_notification_function_exists():
    assert callable(send_notification)


def test_send_notification_returns_false_when_credentials_missing(monkeypatch):
    monkeypatch.setattr("email_notification.GMAIL_ADDRESS", None)
    monkeypatch.setattr("email_notification.GMAIL_APP_PASSWORD", None)
    monkeypatch.setattr("email_notification.NOTIFICATION_EMAIL", None)

    result = send_notification(
        "Test notification",
        "This is an automated test."
    )

    assert result is False


def test_send_notification_successfully(monkeypatch):
    class FakeSMTP:
        def __init__(self, server, port):
            self.server = server
            self.port = port

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def starttls(self):
            pass

        def login(self, email, password):
            pass

        def send_message(self, email):
            assert email["Subject"] == "Test notification"
            assert email["To"] == "recipient@gmail.com"

    monkeypatch.setattr("email_notification.GMAIL_ADDRESS", "test@gmail.com")
    monkeypatch.setattr(
        "email_notification.GMAIL_APP_PASSWORD", "fake-password"
    )
    monkeypatch.setattr(
        "email_notification.NOTIFICATION_EMAIL", "recipient@gmail.com"
    )
    monkeypatch.setattr("email_notification.smtplib.SMTP", FakeSMTP)

    result = send_notification(
        "Test notification",
        "This is a simulated email."
    )

    assert result is True


def test_send_notification_returns_false_when_attachment_missing(
    monkeypatch, tmp_path
):
    monkeypatch.setattr("email_notification.GMAIL_ADDRESS", "test@gmail.com")
    monkeypatch.setattr(
        "email_notification.GMAIL_APP_PASSWORD", "fake-password"
    )
    monkeypatch.setattr(
        "email_notification.NOTIFICATION_EMAIL", "recipient@gmail.com"
    )

    missing_file = tmp_path / "missing_report.txt"

    result = send_notification(
        "Test notification",
        "Testing missing attachment.",
        attachments=[str(missing_file)]
    )

    assert result is False


def test_send_notification_returns_false_when_smtp_fails(monkeypatch):
    class FakeSMTP:
        def __init__(self, server, port):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def starttls(self):
            pass

        def login(self, email, password):
            raise smtplib.SMTPAuthenticationError(
                535, b"Authentication failed"
            )

    monkeypatch.setattr("email_notification.GMAIL_ADDRESS", "test@gmail.com")
    monkeypatch.setattr(
        "email_notification.GMAIL_APP_PASSWORD", "fake-password"
    )
    monkeypatch.setattr(
        "email_notification.NOTIFICATION_EMAIL", "recipient@gmail.com"
    )
    monkeypatch.setattr("email_notification.smtplib.SMTP", FakeSMTP)

    result = send_notification(
        "Test notification",
        "Testing SMTP failure."
    )

    assert result is False
