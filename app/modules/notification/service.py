"""Render mẫu email trước khi gửi qua SMTP."""

import re
from collections.abc import Mapping
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .smtp import send_message


class EmailService:
    def __init__(self) -> None:
        self.environment = Environment(
            loader=FileSystemLoader(Path(__file__).parent / "templates" / "email"),
            autoescape=False,
            undefined=StrictUndefined,
            keep_trailing_newline=False,
        )

    def render(self, template: str, data: Mapping[str, object]) -> tuple[str, str]:
        if not re.fullmatch(r"[a-z0-9_]+", template):
            raise ValueError("Invalid email template name")
        subject = self.environment.get_template(f"{template}.subject.txt").render(data).strip()
        if "\n" in subject or "\r" in subject:
            raise ValueError("Email subject must be a single line")
        body = self.environment.get_template(f"{template}.body.txt").render(data)
        return subject, body

    async def send(self, to: str, template: str, data: Mapping[str, object]) -> None:
        subject, body = self.render(template, data)
        await send_message(to, subject, body)
