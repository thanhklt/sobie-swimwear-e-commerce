"""Cấu hình Jinja dùng chung để render HTML phía server.

Thư mục template: layout chung ở app/shared/web/templates, trang lỗi ở app/error/templates.
"""

from pathlib import Path
from datetime import timedelta, timezone

from fastapi.templating import Jinja2Templates

_APP_DIR = Path(__file__).resolve().parents[2]

templates = Jinja2Templates(
    directory=[
        _APP_DIR / "modules" / "catalog" / "templates",
        _APP_DIR / "shared" / "web" / "templates",
        _APP_DIR / "error" / "templates",
    ]
)

templates.env.filters["vntime"] = lambda value: value.astimezone(timezone(timedelta(hours=7), "Asia/Ho_Chi_Minh")).strftime("%d/%m/%Y %H:%M")
