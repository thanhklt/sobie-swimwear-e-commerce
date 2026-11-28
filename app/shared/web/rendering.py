"""Cấu hình Jinja dùng chung để render HTML phía server.

Layout chung và trang lỗi dùng tên trần. Template của module dùng tiền tố module.
"""

from pathlib import Path

from fastapi.templating import Jinja2Templates
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PrefixLoader

from app.config.store import STORE_HOTLINE, STORE_SHIPPING_FEE, STORE_ZALO_URL

_APP_DIR = Path(__file__).resolve().parents[2]
_modules: dict[str, FileSystemLoader] = {}

templates = Jinja2Templates(
    env=Environment(
        autoescape=True,
        loader=ChoiceLoader([
            FileSystemLoader([
                _APP_DIR / "shared" / "web" / "templates",
                _APP_DIR / "error" / "templates",
            ]),
            PrefixLoader(_modules),
        ]),
    ),
)


def format_vnd(amount: int) -> str:
    return f"{amount:,}".replace(",", ".") + "₫"


templates.env.filters["vnd"] = format_vnd
templates.env.globals["store"] = {
    "hotline": STORE_HOTLINE,
    "zalo_url": STORE_ZALO_URL,
    "shipping_fee": STORE_SHIPPING_FEE,
}


def register_templates(module: str, directory: Path) -> None:
    _modules[module] = FileSystemLoader(directory)
