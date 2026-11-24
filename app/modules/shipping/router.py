"""Thao tác bàn giao UC-40 dành cho nhân viên."""

from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.modules.identity.session import Role
from app.modules.shipping import service
from app.shared.web.session import require_roles

router = APIRouter(tags=["shipping"])
templates = Jinja2Templates(directory=Path(__file__).with_name("templates"))
employee_only = require_roles(Role.EMPLOYEE, login_route="portal_login")
_NO_STORE = {"Cache-Control": "no-store", "Vary": "HX-Request"}


async def _db():
    from app.shared.database.engine import session_factory

    async with session_factory() as db:
        yield db


def _same_origin(request: Request) -> bool:
    origin = request.headers.get("origin")
    return origin is not None and origin.rstrip("/") == str(request.base_url).rstrip("/")


@router.get("/admin/shipping", response_class=HTMLResponse, name="shipping_handoff")
async def shipping_handoff(
    request: Request,
    error: str | None = None,
    q: str | None = None,
    _employee=Depends(employee_only),
    db=Depends(_db),
):
    orders = await service.list_orders_ready_for_handoff(db, q=q)
    return templates.TemplateResponse(
        request,
        "handoff.html",
        {"orders": orders, "error": error, "q": q or ""},
        headers=_NO_STORE,
    )


@router.post("/admin/shipping/{order_code}/handoff", name="shipping_handoff_order")
async def shipping_handoff_order(
    order_code: str,
    request: Request,
    employee=Depends(employee_only),
    db=Depends(_db),
):
    if not _same_origin(request):
        return HTMLResponse("Yêu cầu không hợp lệ.", status_code=403, headers=_NO_STORE)
    try:
        await service.handoff_order(db, order_code, employee.account_key)
    except LookupError as exc:
        # UC-40 E2 — must stay distinct from E1 status message.
        return RedirectResponse(
            f"/admin/shipping?error={quote(str(exc), safe='')}",
            status_code=303,
            headers=_NO_STORE,
        )
    except ValueError as exc:
        # UC-40 E1 — report actual status (e.g. already "Chờ lấy hàng").
        return RedirectResponse(
            f"/admin/shipping?error={quote(str(exc), safe='')}",
            status_code=303,
            headers=_NO_STORE,
        )
    return RedirectResponse("/admin/shipping", status_code=303, headers=_NO_STORE)
