"""Cấu hình Jinja dùng chung để render HTML phía server.

Thư mục template: layout chung ở app/shared/web/templates, trang lỗi ở app/error/templates.
"""

from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi.templating import Jinja2Templates

_APP_DIR = Path(__file__).resolve().parents[2]

templates = Jinja2Templates(
    directory=[
        _APP_DIR / "shared" / "web" / "templates",
        _APP_DIR / "error" / "templates",
        _APP_DIR / "modules" / "inventory" / "templates",
    ]
)


def _inventory_time(value):
    return value.astimezone(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%d/%m/%Y %H:%M")


templates.env.filters["inventory_time"] = _inventory_time
