"""Tầng Route của module ordering: nhận request, kiểm tra dữ liệu đầu vào, gọi service,
trả response.
Không gọi repository hoặc database trực tiếp. Chưa triển khai.
"""

from urllib.parse import urlencode

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.error.exceptions import SessionAccessError
from app.modules.identity.facade import Role
from app.modules.ordering.service import preview_checkout
from app.shared.web.rendering import templates

router = APIRouter(prefix="/api/v1/ordering")
_NO_STORE = {"Cache-Control": "no-store"}


@router.get("/checkout", response_class=HTMLResponse)
async def checkout(request: Request):
    actor = request.state.auth_session
    if actor is None:
        login = request.url_for("storefront_login").path
        query = urlencode({"return_to": request.url_for("checkout").path})
        return RedirectResponse(f"{login}?{query}", status_code=303, headers=_NO_STORE)
    if actor.role != Role.CUSTOMER:
        raise SessionAccessError(status_code=403)
    items = await preview_checkout(request.app.state.shopping_session_factory, actor.account_key)
    return templates.TemplateResponse(
        request, "ordering/checkout.html", {"items": items},
        headers=_NO_STORE | {"Referrer-Policy": "strict-origin"},
    )
