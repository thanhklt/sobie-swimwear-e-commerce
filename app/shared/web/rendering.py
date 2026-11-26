"""Cấu hình Jinja dùng chung để render HTML phía server.

Layout chung và trang lỗi dùng tên trần. Template của module dùng tiền tố module.
"""

from pathlib import Path

from fastapi.templating import Jinja2Templates
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PrefixLoader

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


def register_templates(module: str, directory: Path) -> None:
    _modules[module] = FileSystemLoader(directory)
