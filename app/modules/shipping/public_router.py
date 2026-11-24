"""Public carrier simulator endpoints, served by the standalone shipping app."""

from pathlib import Path
from urllib.parse import parse_qs, quote

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.modules.shipping import service

router = APIRouter(tags=["public-shipping"])
templates = Jinja2Templates(directory=Path(__file__).with_name("templates"))
_NO_STORE = {"Cache-Control": "no-store", "Vary": "HX-Request"}


async def _db():
    from app.shared.database.engine import session_factory

    async with session_factory() as db:
        yield db


def _same_origin(request: Request) -> bool:
    origin = request.headers.get("origin")
    return origin is not None and origin.rstrip("/") == str(request.base_url).rstrip("/")


@router.get("/", response_class=HTMLResponse, name="shipping_simulator")
@router.get("/shipping/", response_class=HTMLResponse, name="shipping_simulator_legacy")
async def shipping_simulator(
    request: Request,
    error: str | None = None,
    q: str | None = None,
    status: str | None = None,
    db=Depends(_db),
):
    orders = await service.list_simulator_orders(db, q=q, status=status)
    return templates.TemplateResponse(
        request,
        "shipping.html",
        {"orders": orders, "error": error, "q": q or "", "status": status or ""},
        headers=_NO_STORE,
    )


@router.post("/orders/{order_code}/status", name="shipping_update_status")
@router.post("/shipping/orders/{order_code}/status", name="shipping_update_status_legacy")
async def shipping_update_status(order_code: str, request: Request, db=Depends(_db)):
    if not _same_origin(request):
        return HTMLResponse("Yêu cầu không hợp lệ.", status_code=403, headers=_NO_STORE)
    form = parse_qs((await request.body()).decode("utf-8"), keep_blank_values=True)
    action = form.get("action", [""])[0]
    try:
        await service.update_simulator_status(db, order_code, action)
    except (LookupError, ValueError) as exc:
        return RedirectResponse(f"/?error={quote(str(exc), safe='')}", status_code=303, headers=_NO_STORE)
    return RedirectResponse("/", status_code=303, headers=_NO_STORE)
