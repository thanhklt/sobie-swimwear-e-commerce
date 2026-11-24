"""Gửi OTP qua SMTP sử dụng TLS."""

import asyncio
from email.message import EmailMessage
from smtplib import SMTP, SMTP_SSL
from ssl import create_default_context

from app.config.settings import Config


def _send_otp(email: str, otp: str) -> None:
    if not Config.SMTP_HOST or not Config.SMTP_FROM:
        raise RuntimeError("SMTP_HOST and SMTP_FROM are required for registration")
    if bool(Config.SMTP_USERNAME) != (Config.SMTP_PASSWORD is not None):
        raise RuntimeError("SMTP credentials must be configured together")

    message = EmailMessage()
    message["From"] = Config.SMTP_FROM
    message["To"] = email
    message["Subject"] = "Mã xác minh Sobie"
    message.set_content(f"Mã xác minh Sobie của bạn là {otp}. Mã có hiệu lực trong 5 phút.")

    context = create_default_context()
    if Config.SMTP_SECURITY == "ssl":
        connection = SMTP_SSL(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10, context=context)
    else:
        connection = SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10)

    try:
        if Config.SMTP_SECURITY == "starttls":
            connection.starttls(context=context)
        if Config.SMTP_USERNAME and Config.SMTP_PASSWORD:
            connection.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        connection.send_message(message, from_addr=Config.SMTP_FROM, to_addrs=[email])
    finally:
        connection.close()


async def send_registration_otp(email: str, otp: str) -> None:
    await asyncio.to_thread(_send_otp, email, otp)
