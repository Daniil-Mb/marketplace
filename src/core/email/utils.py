import smtplib
from email.message import EmailMessage

from src.core.config import get_settings


def send_email(
    *,
    recipient: str,
    subject: str,
    body: str,
) -> None:
    settings = get_settings()
    message = EmailMessage()

    message["From"] = settings.mail_from
    message["To"] = recipient
    message["Subject"] = subject

    message.set_content(body)

    with smtplib.SMTP(
        settings.mail_host,
        settings.mail_port,
    ) as smtp:
        smtp.send_message(message)
