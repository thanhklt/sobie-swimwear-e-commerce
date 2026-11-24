"""Các endpoint UC-28, UC-29, UC-30 (quản trị) và dịch vụ dùng bởi UC-31."""

from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, quote

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from app.modules.catalog import service as catalog_service
from app.modules.identity.session import Role
from app.modules.promotion import service
from app.shared.web.session import require_roles

router = APIRouter(prefix="/admin/promotions", tags=["promotion"])
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


def _error_url(message: str, field: str | None = None, kind: str | None = None) -> str:
    url = "/admin/promotions?error=" + quote(message, safe="")
    if field:
        url += "&field=" + quote(field, safe="")
    if kind:
        url += "&kind=" + quote(kind, safe="")
    return url


def _raw_form(request_body: bytes) -> dict[str, str]:
    raw = parse_qs(request_body.decode("utf-8"), keep_blank_values=True)
    return {key: values[0] for key, values in raw.items()}


@router.get("", response_class=HTMLResponse, name="promotion_admin")
async def promotion_admin(
    request: Request, kind: str | None = None, date_from: str | None = None,
    date_to: str | None = None, error: str | None = None, field: str | None = None,
    _employee=Depends(employee_only), db=Depends(_db),
):
    try:
        date_from = date.fromisoformat(date_from.strip()) if date_from and date_from.strip() else None
        date_to = date.fromisoformat(date_to.strip()) if date_to and date_to.strip() else None
    except ValueError:
        date_from = date_to = None
        error = "Ngày lọc không hợp lệ."
    if kind == "PRODUCT":
        date_from = date_to = None
    if date_from and date_to and date_from > date_to:
        error = "Ngày bắt đầu lọc phải trước hoặc bằng ngày kết thúc."
    rows = await service.list_promotions(db, kind if kind in {"PRODUCT", "ORDER", "CODE"} else None)
    products = await catalog_service.active_products_for_promotion(db)
    if date_from or date_to:
        rows = [r for r in rows if r["promotion_type"] != "PRODUCT" and (
            (date_to is None or r["start_date"] is None or r["start_date"].date() <= date_to)
            and (date_from is None or r["end_date"] is None or r["end_date"].date() >= date_from)
        )]
    return templates.TemplateResponse(request, "promotions.html", {
        "promotions": rows, "kind": kind or "", "date_from": date_from or "",
        "date_to": date_to or "", "error": error, "error_field": field or "",
        "products": products,
    }, headers=_NO_STORE)


@router.post("/create", name="promotion_create")
async def promotion_create(
    request: Request, _employee=Depends(employee_only), db=Depends(_db),
):
    if not _same_origin(request):
        return HTMLResponse("Yêu cầu không hợp lệ.", status_code=403, headers=_NO_STORE)
    form = _raw_form(await request.body())
    try:
        await service.create_promotion(db, form)
    except service.PromotionValidationError as exc:
        return RedirectResponse(_error_url(str(exc), exc.field, form.get("promotion_type")), status_code=303, headers=_NO_STORE)
    except (ValueError, KeyError, ArithmeticError, IntegrityError) as exc:
        message = "Mã voucher đã tồn tại (không phân biệt hoa thường)." if isinstance(exc, IntegrityError) else str(exc) or "Dữ liệu chưa hợp lệ."
        return RedirectResponse(_error_url(message, "code" if isinstance(exc, IntegrityError) else None, form.get("promotion_type")), status_code=303, headers=_NO_STORE)
    return RedirectResponse("/admin/promotions", status_code=303, headers=_NO_STORE)


@router.post("/validate", name="promotion_validate")
async def promotion_validate(
    request: Request, _employee=Depends(employee_only), db=Depends(_db),
):
    """Preflight form validation so invalid values never reach confirmation."""
    if not _same_origin(request):
        return JSONResponse({"errors": {"_form": "Yêu cầu không hợp lệ."}}, status_code=403, headers=_NO_STORE)
    try:
        await service.validate_promotion(db, _raw_form(await request.body()))
    except service.PromotionValidationError as exc:
        return JSONResponse({"errors": {exc.field: str(exc)}}, status_code=422, headers=_NO_STORE)
    except (ValueError, KeyError, ArithmeticError) as exc:
        return JSONResponse({"errors": {"_form": str(exc) or "Dữ liệu chưa hợp lệ."}}, status_code=422, headers=_NO_STORE)
    return JSONResponse({"valid": True}, headers=_NO_STORE)


@router.post("/quote-preview", name="promotion_quote_preview")
async def promotion_quote_preview(
    request: Request, _employee=Depends(employee_only), db=Depends(_db),
):
    """Preview UC-31 for employees without consuming a promotion or creating an order."""
    if not _same_origin(request):
        return JSONResponse({"error": "Yêu cầu không hợp lệ."}, status_code=403, headers=_NO_STORE)
    form = _raw_form(await request.body())
    try:
        subtotal = int(form.get("subtotal") or 0)
    except (TypeError, ValueError):
        return JSONResponse({"error": "Tạm tính không hợp lệ."}, status_code=422, headers=_NO_STORE)
    if subtotal < 0:
        return JSONResponse({"error": "Tạm tính phải lớn hơn hoặc bằng 0 đồng."}, status_code=422, headers=_NO_STORE)
    voucher = (form.get("voucher_code") or "").strip() or None
    try:
        quote = await service.quote_order_discount(db, subtotal, voucher_code=voucher)
    except Exception:
        return JSONResponse(
            {"error": "Không tính được ưu đãi lúc này. Vui lòng thử lại."},
            status_code=500,
            headers=_NO_STORE,
        )
    payload = {
        "subtotal": subtotal,
        "selected_discount": int(quote["selected_discount"]),
        "selected_source": quote["selected_source"],
        "selected_promotion_id": quote.get("selected_promotion_id"),
        "selected_promotion_label": quote["selected_promotion_label"],
        "payable_before_shipping": subtotal - int(quote["selected_discount"]),
        "notice": quote["notice"],
    }
    return JSONResponse(payload, headers=_NO_STORE)


@router.post("/{promotion_id}/end", name="promotion_end")
async def promotion_end(
    promotion_id: str, request: Request,
    _employee=Depends(employee_only), db=Depends(_db),
):
    if not _same_origin(request):
        return HTMLResponse("Yêu cầu không hợp lệ.", status_code=403, headers=_NO_STORE)
    if not await service.end_promotion(db, promotion_id):
        return RedirectResponse(_error_url("Khuyến mãi không tồn tại hoặc đã kết thúc."), status_code=303, headers=_NO_STORE)
    return RedirectResponse("/admin/promotions", status_code=303, headers=_NO_STORE)
