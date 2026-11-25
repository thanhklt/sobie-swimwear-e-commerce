"""Tầng Route của module inventory: nhận request, kiểm tra dữ liệu đầu vào, gọi service,
trả response.
Không gọi repository hoặc database trực tiếp.
"""

from itertools import zip_longest
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse

from app.error.exceptions import SessionAccessError
from app.modules.identity.session import AuthenticatedSession, Role
from app.modules.inventory import service
from app.modules.inventory.schemas import ReceiptInput, SupplierInput
from app.shared.web.rendering import templates
from app.shared.web.session import require_roles

PREFIX = "/api/v1/inventory/staff"
HEADERS = {"Cache-Control": "no-store", "Vary": "HX-Request"}
_staff = require_roles(Role.EMPLOYEE, login_route="portal_login")


def _render(request: Request, view: str, context: dict | None = None, *, status: int = 200):
    name = "inventory/content.html" if request.headers.get("HX-Request") == "true" else "inventory/page.html"
    return templates.TemplateResponse(request, name, {"view": view, **(context or {})}, status_code=status, headers=HEADERS)


def _error(request: Request, exc: service.InventoryError):
    return _render(request, "error", {"message": exc.message, "errors": exc.field_errors}, status=exc.status_code)


async def _origin(request: Request):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        try:
            origin = urlsplit(request.headers.get("Origin", ""))
            expected = urlsplit(str(request.url))
            defaults = {"http": 80, "https": 443}
            valid = (origin.scheme in defaults and not any((origin.path, origin.query, origin.fragment))
                     and origin.username is None and origin.password is None
                     and (origin.scheme, origin.hostname, origin.port or defaults[origin.scheme])
                     == (expected.scheme, expected.hostname, expected.port or defaults.get(expected.scheme)))
        except ValueError:
            valid = False
        if not valid:
            raise SessionAccessError(status_code=403)


router = APIRouter(prefix=PREFIX, dependencies=[Depends(_staff), Depends(_origin)])


def _uuid(value: str, label: str) -> UUID:
    try:
        return UUID(value)
    except (ValueError, TypeError, AttributeError) as exc:
        raise service.InventoryError(f"{label} không hợp lệ") from exc


def _page(request: Request) -> int:
    raw = request.query_params.get("page", "1")
    if len(raw) > 10 or not raw.isascii() or not raw.isdecimal() or not 1 <= int(raw) <= 2_147_483_647:
        raise service.InventoryError("Trang không hợp lệ")
    return int(raw)


async def _form(request: Request):
    try:
        form = await request.form()
    except (HTTPException, ValueError) as exc:
        raise service.InventoryError("Dữ liệu biểu mẫu không hợp lệ") from exc
    if any(not isinstance(value, str) for _, value in form.multi_items()):
        raise service.InventoryError("Biểu mẫu không chấp nhận tệp đính kèm")
    return form


def _validation(exc: ValidationError) -> dict[str, str]:
    return {".".join(map(str, error["loc"])) or "form": error["msg"] for error in exc.errors()}


def _redirect(path: str):
    return RedirectResponse(path, status_code=303, headers=HEADERS)


@router.get("/suppliers", name="inventory_suppliers")
async def suppliers(request: Request):
    try:
        return _render(request, "suppliers", await service.list_suppliers(q=request.query_params.get("q", ""), page=_page(request)))
    except service.InventoryError as exc:
        return _error(request, exc)


@router.get("/suppliers/new", name="inventory_supplier_new")
async def supplier_new(request: Request):
    return _render(request, "supplier_form", {"supplier": {}, "form": {}})


async def _save_supplier(request: Request, supplier_key: str | None = None):
    raw, supplier = {}, {}
    try:
        key = _uuid(supplier_key, "Nhà cung cấp") if supplier_key is not None else None
        if key is not None:
            supplier = await service.get_supplier(key)
        raw = dict(await _form(request))
        data = SupplierInput.model_validate({field: raw.get(field, "") for field in ("name", "phone_number", "email", "address")})
        await service.save_supplier(data, supplier_key=key)
        return _redirect(f"{PREFIX}/suppliers")
    except ValidationError as exc:
        errors, message, status = _validation(exc), "Dữ liệu nhà cung cấp không hợp lệ", 400
    except service.InventoryError as exc:
        if exc.status_code == 404:
            return _error(request, exc)
        errors, message, status = exc.field_errors, exc.message, exc.status_code
    return _render(request, "supplier_form", dict(supplier=supplier, form=raw, errors=errors, message=message), status=status)


@router.post("/suppliers/new", name="inventory_supplier_create")
async def supplier_create(request: Request):
    return await _save_supplier(request)


@router.get("/suppliers/{supplier_key}/edit", name="inventory_supplier_edit")
async def supplier_edit(request: Request, supplier_key: str):
    try:
        return _render(request, "supplier_form", {"supplier": await service.get_supplier(_uuid(supplier_key, "Nhà cung cấp")), "form": {}})
    except service.InventoryError as exc:
        return _error(request, exc)


@router.post("/suppliers/{supplier_key}/edit", name="inventory_supplier_update")
async def supplier_update(request: Request, supplier_key: str):
    return await _save_supplier(request, supplier_key)


async def _supplier_action(request: Request, supplier_key: str, action):
    try:
        key = _uuid(supplier_key, "Nhà cung cấp")
        if (await _form(request)).get("confirm") != "yes":
            raise service.InventoryError("Vui lòng xác nhận thao tác")
        await action(key)
        return _redirect(f"{PREFIX}/suppliers")
    except service.InventoryError as exc:
        return _error(request, exc)


@router.post("/suppliers/{supplier_key}/deactivate", name="inventory_supplier_deactivate")
async def supplier_deactivate(request: Request, supplier_key: str):
    return await _supplier_action(request, supplier_key, service.deactivate_supplier)


@router.post("/suppliers/{supplier_key}/delete", name="inventory_supplier_delete")
async def supplier_delete(request: Request, supplier_key: str):
    return await _supplier_action(request, supplier_key, service.delete_supplier)


@router.get("/goods-receipts", name="inventory_receipts")
async def receipts(request: Request):
    try:
        supplier_key = request.query_params.get("supplier_key")
        return _render(request, "receipts", await service.list_receipts(
            status=request.query_params.get("status") or None,
            supplier_key=_uuid(supplier_key, "Nhà cung cấp") if supplier_key else None, page=_page(request)))
    except service.InventoryError as exc:
        return _error(request, exc)


@router.get("/goods-receipts/new", name="inventory_receipt_new")
async def receipt_new(request: Request):
    try:
        return _render(request, "receipt_form", {"receipt": {}, "lines": [{}], **(await service.receipt_form_data())})
    except service.InventoryError as exc:
        return _error(request, exc)


async def _save_receipt(request: Request, session: AuthenticatedSession, receipt_key: str | None = None):
    raw, lines, context = {}, [], {"receipt": {}}
    try:
        key = _uuid(receipt_key, "Phiếu nhập") if receipt_key is not None else None
        if key is not None:
            context = await service.get_receipt(key)
        raw = await _form(request)
        arrays = [raw.getlist(field) for field in ("variant_key", "quantity", "unit_price")]
        lines = [dict(zip(("variant_key", "quantity", "unit_price"), values))
                 for values in zip_longest(*arrays, fillvalue="")]
        if len({len(values) for values in arrays}) != 1:
            raise service.InventoryError("Dữ liệu các dòng không đầy đủ", field_errors={"lines": "Mỗi dòng phải có biến thể, số lượng và giá nhập"})
        data = ReceiptInput(supplier_key=raw.get("supplier_key", ""), lines=lines)
        receipt = await service.save_receipt(data, session.account_key, receipt_key=key)
        return _redirect(f"{PREFIX}/goods-receipts/{receipt['goods_receipt_key']}")
    except ValidationError as exc:
        errors, message, status = _validation(exc), "Dữ liệu phiếu nhập không hợp lệ", 400
    except service.InventoryError as exc:
        if not raw:
            return _error(request, exc)
        errors, message, status = exc.field_errors, exc.message, exc.status_code
    try:
        context.update(await service.receipt_form_data())
    except service.InventoryError:
        context.setdefault("suppliers", [])
        context.setdefault("variants", [])
    context.update(form=dict(raw), lines=lines, errors=errors, message=message)
    return _render(request, "receipt_form", context, status=status)


@router.post("/goods-receipts/new", name="inventory_receipt_create")
async def receipt_create(request: Request, session: AuthenticatedSession = Depends(_staff)):
    return await _save_receipt(request, session)


@router.get("/goods-receipts/{receipt_key}", name="inventory_receipt_detail")
async def receipt_detail(request: Request, receipt_key: str):
    try:
        return _render(request, "receipt_detail", await service.get_receipt(_uuid(receipt_key, "Phiếu nhập")))
    except service.InventoryError as exc:
        return _error(request, exc)


@router.post("/goods-receipts/{receipt_key}/edit", name="inventory_receipt_update")
async def receipt_update(request: Request, receipt_key: str, session: AuthenticatedSession = Depends(_staff)):
    return await _save_receipt(request, session, receipt_key)


async def _receipt_action(request: Request, receipt_key: str, action):
    try:
        key = _uuid(receipt_key, "Phiếu nhập")
        if (await _form(request)).get("confirm") != "yes":
            raise service.InventoryError("Vui lòng xác nhận thao tác")
        await action(key)
        return _redirect(f"{PREFIX}/goods-receipts/{key}")
    except service.InventoryError as exc:
        return _error(request, exc)


@router.post("/goods-receipts/{receipt_key}/cancel", name="inventory_receipt_cancel")
async def receipt_cancel(request: Request, receipt_key: str):
    return await _receipt_action(request, receipt_key, service.cancel_receipt)


@router.post("/goods-receipts/{receipt_key}/confirm", name="inventory_receipt_confirm")
async def receipt_confirm(request: Request, receipt_key: str):
    return await _receipt_action(request, receipt_key, service.confirm_receipt)


@router.get("/stock", name="inventory_stock")
async def stock(request: Request):
    try:
        category_key = request.query_params.get("category_key")
        return _render(request, "stock", await service.list_stock(
            q=request.query_params.get("q", ""), category_key=_uuid(category_key, "Danh mục") if category_key else None,
            page=_page(request)))
    except service.InventoryError as exc:
        return _error(request, exc)
