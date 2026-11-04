
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
