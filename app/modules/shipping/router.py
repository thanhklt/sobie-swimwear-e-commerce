"""Website giao hàng giả lập và thao tác bàn giao UC-36/UC-40."""

from pathlib import Path
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.modules.identity.session import Role
from app.modules.ordering import service as ordering_service
from app.shared.web.session import require_roles

router = APIRouter(tags=["shipping"])
templates = Jinja2Templates(directory=Path(__file__).with_name("templates"))
employee_only = require_roles(Role.EMPLOYEE, login_route="portal_login")


async def _db():
    from app.shared.database.engine import session_factory

    async with session_factory() as db:
        yield db


def _same_origin(request: Request) -> bool:
    origin = request.headers.get("origin")
    return origin is not None and origin.rstrip("/") == str(request.base_url).rstrip("/")


@router.get("/shipping/", response_class=HTMLResponse, name="shipping_simulator")
async def shipping_simulator(request: Request, error: str | None = None, db=Depends(_db)):
    orders = await ordering_service.list_shipping_orders(db)
    return templates.TemplateResponse(request, "shipping.html", {"orders": orders, "error": error})


@router.post("/shipping/orders/{order_code}/status", name="shipping_update_status")
async def shipping_update_status(order_code: str, request: Request, db=Depends(_db)):
    if not _same_origin(request):
        return HTMLResponse("Yêu cầu không hợp lệ.", status_code=403)
    form = parse_qs((await request.body()).decode("utf-8"))
    action = form.get("action", [""])[0]
    try:
        await ordering_service.update_shipping_status(db, order_code, action)
    except LookupError as exc:
        return RedirectResponse(f"/shipping/?error={exc}", status_code=303)
    except ValueError as exc:
        return RedirectResponse(f"/shipping/?error={exc}", status_code=303)
    return RedirectResponse("/shipping/", status_code=303)


@router.get("/admin/shipping", response_class=HTMLResponse, name="shipping_handoff")
async def shipping_handoff(request: Request, error: str | None = None,
                           _employee=Depends(employee_only), db=Depends(_db)):
    orders = await ordering_service.list_confirmed_orders(db)
    return templates.TemplateResponse(request, "handoff.html", {"orders": orders, "error": error})


@router.post("/admin/shipping/{order_code}/handoff", name="shipping_handoff_order")
async def shipping_handoff_order(order_code: str, request: Request,
                                 employee=Depends(employee_only), db=Depends(_db)):
    if not _same_origin(request):
        return HTMLResponse("Yêu cầu không hợp lệ.", status_code=403)
    if not await ordering_service.handoff_order(db, order_code, employee.account_key):
        return RedirectResponse("/admin/shipping?error=Đơn không tồn tại hoặc không ở trạng thái Đã xác nhận.", status_code=303)
    return RedirectResponse("/admin/shipping", status_code=303)
