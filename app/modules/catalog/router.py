"""Tầng Route của module catalog: nhận request, kiểm tra dữ liệu đầu vào, gọi service,
trả response.
Không gọi repository hoặc database trực tiếp.
"""

from fastapi import Request
from fastapi.responses import Response

from app.modules.catalog import service
from app.shared.web.rendering import templates


def storefront_home(request: Request) -> Response:
    return templates.TemplateResponse(
        request,
        "catalog/home.html",
        {"home": service.get_home_page()},
        headers={
            "Cache-Control": "private, no-cache",
            "Referrer-Policy": "strict-origin",
            "Vary": "Accept",
        },
    )
