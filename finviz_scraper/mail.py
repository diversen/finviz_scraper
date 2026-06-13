from email.message import EmailMessage
import smtplib
import ssl

from finviz_scraper.logging import get_log
from settings import settings


log = get_log()


def send_mail(subject: str, body: str) -> bool:
    """Send a plain-text email using SMTP settings from settings.py."""
    smtp_settings = settings.get("smtp", {})
    host = smtp_settings.get("host")
    recipients = smtp_settings.get("to", [])
    sender = smtp_settings.get("from")

    if isinstance(recipients, str):
        recipients = [recipients]

    if not host or not sender or not recipients:
        log.debug("SMTP report skipped because host, from, or to is not configured")
        return False

    port = smtp_settings.get("port", 587)
    username = smtp_settings.get("username")
    password = smtp_settings.get("password")
    use_tls = smtp_settings.get("use_tls", True)
    use_ssl = smtp_settings.get("use_ssl", False)
    timeout = smtp_settings.get("timeout", 30)

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(body)

    try:
        if use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, timeout=timeout, context=context) as smtp:
                if username and password:
                    smtp.login(username, password)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(host, port, timeout=timeout) as smtp:
                if use_tls:
                    context = ssl.create_default_context()
                    smtp.starttls(context=context)
                if username and password:
                    smtp.login(username, password)
                smtp.send_message(message)
    except Exception:
        log.exception("Failed sending SMTP report")
        return False

    log.info("Sent SMTP report to %s", ", ".join(recipients))
    return True


def send_report(lines: list[str]) -> bool:
    subject = settings.get("smtp", {}).get("subject", "Finviz scraper report")
    body = "\n".join(lines)
    return send_mail(subject, body)
