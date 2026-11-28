"""Cửa công khai để gửi thông báo qua email."""

from collections.abc import Mapping
from functools import lru_cache

from .service import EmailService


@lru_cache(maxsize=1)
def _email_service() -> EmailService:
    return EmailService()


async def send_email(to: str, template: str, data: Mapping[str, object]) -> None:
    await _email_service().send(to, template, data)
