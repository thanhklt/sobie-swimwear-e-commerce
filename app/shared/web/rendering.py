"""Cấu hình Jinja dùng chung để render HTML phía server.

Thư mục template: layout chung, trang lỗi và dashboard báo cáo.
"""

from pathlib import Path

from fastapi.templating import Jinja2Templates

_APP_DIR = Path(__file__).resolve().parents[2]

templates = Jinja2Templates(
    directory=[
        _APP_DIR / "shared" / "web" / "templates",
        _APP_DIR / "error" / "templates",
        _APP_DIR / "modules" / "reporting" / "templates",
    ]
)
