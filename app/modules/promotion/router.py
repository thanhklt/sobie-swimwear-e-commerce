"""Các endpoint UC-28, UC-29, UC-30 (quản trị) và dịch vụ dùng bởi UC-31."""

from datetime import date
from decimal import Decimal
from pathlib import Path
from urllib.parse import parse_qs, quote

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from app.modules.identity.session import Role
from app.modules.promotion import service
from app.shared.database.transaction import transaction
from app.shared.web.session import require_roles

router = APIRouter(prefix="/admin/promotions", tags=["promotion"])
templates = Jinja2Templates(directory=Path(__file__).with_name("templates"))
employee_only = require_roles(Role.EMPLOYEE, login_route="portal_login")


async def _db():
    from app.shared.database.engine import session_factory

    async with session_factory() as db:
        yield db


def _same_origin(request: Request) -> bool:
    origin = request.headers.get("origin")
    return origin is not None and origin.rstrip("/") == str(request.base_url).rstrip("/")


def _error_url(message: str) -> str:
    return "/admin/promotions?error=" + quote(message, safe="")


@router.get("", response_class=HTMLResponse, name="promotion_admin")
async def promotion_admin(
    request: Request, kind: str | None = None, date_from: date | None = None,
    date_to: date | None = None, error: str | None = None,
    _employee=Depends(employee_only), db=Depends(_db),
):
    if date_from and date_to and date_from > date_to:
        error = "Ngày bắt đầu lọc phải trước hoặc bằng ngày kết thúc."
    rows = await service.list_promotions(db, kind if kind in {"PRODUCT", "ORDER", "CODE"} else None)
    if date_from or date_to:
        rows = [r for r in rows if r["promotion_type"] != "PRODUCT" and (
            (date_to is None or r["start_date"] is None or r["start_date"].date() <= date_to)
            and (date_from is None or r["end_date"] is None or r["end_date"].date() >= date_from)
        )]
    return templates.TemplateResponse(request, "promotions.html", {
        "promotions": rows, "kind": kind or "", "date_from": date_from or "",
        "date_to": date_to or "", "error": error,
    })


@router.post("/create", name="promotion_create")
async def promotion_create(
    request: Request, _employee=Depends(employee_only), db=Depends(_db),
):
    if not _same_origin(request):
        return HTMLResponse("Yêu cầu không hợp lệ.", status_code=403)
    raw = parse_qs((await request.body()).decode("utf-8"), keep_blank_values=True)
    form = {key: values[0] for key, values in raw.items()}
    try:
        form["discount_percentage"] = Decimal(form.get("discount_percentage", ""))
        for key in ("threshold_price", "quantity"):
            form[key] = int(form[key]) if form.get(key) else None
        for key in ("start_date", "end_date"):
            form[key] = date.fromisoformat(form[key]) if form.get(key) else None
        await service.create_promotion(db, form)
    except (ValueError, KeyError, ArithmeticError, IntegrityError) as exc:
        message = "Mã voucher đã tồn tại (không phân biệt hoa thường)." if isinstance(exc, IntegrityError) else str(exc) or "Dữ liệu chưa hợp lệ."
        return RedirectResponse(_error_url(message), status_code=303)
    return RedirectResponse("/admin/promotions", status_code=303)


@router.post("/{promotion_id}/end", name="promotion_end")
async def promotion_end(
    promotion_id: str, request: Request,
    _employee=Depends(employee_only), db=Depends(_db),
):
    if not _same_origin(request):
        return HTMLResponse("Yêu cầu không hợp lệ.", status_code=403)
    if not await service.end_promotion(db, promotion_id):
        return RedirectResponse(_error_url("Khuyến mãi không tồn tại hoặc đã kết thúc."), status_code=303)
    return RedirectResponse("/admin/promotions", status_code=303)
