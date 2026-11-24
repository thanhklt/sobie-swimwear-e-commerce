"""Tầng Route ordering — UI thử SSR (/dev/ordering).

Router chỉ validate input / gọi service / render Jinja. Không gọi repository.
Adapter tạm [GD]: identity demo + DbInventory/DbCatalog đến khi teammate sẵn service.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from decimal import Decimal, InvalidOperation
from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.ordering import adapters, jobs, service
from app.modules.ordering.adapters import DEMO_CUSTOMER_EMAIL, DEMO_EMPLOYEE_EMAIL
from app.modules.ordering.exceptions import OrderingError, PriceChangedError
from app.modules.ordering.schemas import ShippingInfo
from app.modules.shopping.exceptions import ShoppingError
from app.shared.database.engine import session_factory
from app.shared.web.rendering import templates

router = APIRouter(prefix="/dev/ordering", tags=["ordering-dev"])


async def get_db() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]


def _redirect(path: str, *, ok: str | None = None, error: str | None = None, **extra: str) -> RedirectResponse:
    params: dict[str, str] = {}
    if ok:
        params["ok"] = ok
    if error:
        params["error"] = error
    params.update({k: v for k, v in extra.items() if v})
    qs = f"?{urlencode(params)}" if params else ""
    return RedirectResponse(f"{path}{qs}", status_code=303)


def _flash(request: Request) -> dict[str, str | None]:
    return {
        "flash_ok": request.query_params.get("ok"),
        "flash_error": request.query_params.get("error"),
    }


def _shipping_from_form(
    name: str,
    phone: str,
    house_number: str,
    ward: str,
    city: str,
    country: str,
) -> ShippingInfo:
    return ShippingInfo(
        name=name.strip(),
        phone=phone.strip(),
        house_number=house_number.strip(),
        ward=ward.strip(),
        city=city.strip(),
        country=country.strip(),
    )


def _parse_expected_total(raw: str | None) -> Decimal | None:
    if raw is None or not str(raw).strip():
        return None
    try:
        return Decimal(str(raw).strip())
    except InvalidOperation:
        return None


@router.get("")
async def ordering_home(request: Request):
    return templates.TemplateResponse(
        request,
        "ordering_home.html",
        {
            "title": "Thử ordering",
            "demo_customer": DEMO_CUSTOMER_EMAIL,
            "demo_employee": DEMO_EMPLOYEE_EMAIL,
            **_flash(request),
        },
    )


@router.get("/checkout")
async def checkout_page(request: Request, db: DbSession):
    account_key = await adapters.get_account_key_by_email(db, DEMO_CUSTOMER_EMAIL)
    inv = adapters.DbInventoryGateway(db)
    pricing = adapters.DbCatalogPricing(db)
    quote = None
    quote_error = None
    labels: dict = {}
    cart_empty = False
    try:
        quote = await service.build_quote(
            db, account_key=account_key, inventory=inv, pricing=pricing
        )
        labels = {
            ln.variant_key: await pricing.get_variant_label(ln.variant_key)
            for ln in quote.lines
        }
    except (OrderingError, ShoppingError) as exc:
        quote_error = getattr(exc, "message", str(exc))
        cart_empty = True

    new_total = request.query_params.get("new_total")
    return templates.TemplateResponse(
        request,
        "ordering_checkout.html",
        {
            "title": "Đặt hàng",
            "demo_customer": DEMO_CUSTOMER_EMAIL,
            "quote": quote,
            "labels": labels,
            "quote_error": quote_error,
            "cart_empty": cart_empty,
            "new_total": new_total,
            "default_shipping": {
                "name": "Khách Hàng Demo",
                "phone": "0900000003",
                "house_number": "273 An Dương Vương",
                "ward": "Phường Chợ Quán",
                "city": "TP. Hồ Chí Minh",
                "country": "Việt Nam",
            },
            **_flash(request),
        },
    )


@router.post("/checkout/cod")
async def checkout_cod(
    db: DbSession,
    name: Annotated[str, Form()],
    phone: Annotated[str, Form()],
    house_number: Annotated[str, Form()],
    ward: Annotated[str, Form()],
    city: Annotated[str, Form()],
    country: Annotated[str, Form()],
    expected_total: Annotated[str | None, Form()] = None,
):
    try:
        account_key = await adapters.get_account_key_by_email(db, DEMO_CUSTOMER_EMAIL)
        order = await service.place_cod_order(
            db,
            account_key=account_key,
            shipping=_shipping_from_form(
                name, phone, house_number, ward, city, country
            ),
            inventory=adapters.DbInventoryGateway(db),
            pricing=adapters.DbCatalogPricing(db),
            expected_total=_parse_expected_total(expected_total),
        )
        return _redirect(
            f"/dev/ordering/orders/{order.order_code}",
            ok=f"Đã tạo đơn COD {order.order_code}",
        )
    except PriceChangedError as exc:
        return _redirect(
            "/dev/ordering/checkout",
            error=exc.message,
            new_total=str(exc.new_total),
        )
    except OrderingError as exc:
        return _redirect("/dev/ordering/checkout", error=exc.message)


@router.post("/checkout/qr")
async def checkout_qr(
    db: DbSession,
    name: Annotated[str, Form()],
    phone: Annotated[str, Form()],
    house_number: Annotated[str, Form()],
    ward: Annotated[str, Form()],
    city: Annotated[str, Form()],
    country: Annotated[str, Form()],
    expected_total: Annotated[str | None, Form()] = None,
):
    try:
        account_key = await adapters.get_account_key_by_email(db, DEMO_CUSTOMER_EMAIL)
        order = await service.place_qr_order(
            db,
            account_key=account_key,
            shipping=_shipping_from_form(
                name, phone, house_number, ward, city, country
            ),
            inventory=adapters.DbInventoryGateway(db),
            pricing=adapters.DbCatalogPricing(db),
            expected_total=_parse_expected_total(expected_total),
        )
        return _redirect(
            f"/dev/ordering/orders/{order.order_code}",
            ok=f"Đã tạo đơn QR {order.order_code}",
        )
    except PriceChangedError as exc:
        return _redirect(
            "/dev/ordering/checkout",
            error=exc.message,
            new_total=str(exc.new_total),
        )
    except OrderingError as exc:
        return _redirect("/dev/ordering/checkout", error=exc.message)


@router.get("/orders")
async def orders_list(request: Request, db: DbSession):
    account_key = await adapters.get_account_key_by_email(db, DEMO_CUSTOMER_EMAIL)
    views, total = await service.list_customer_orders(db, account_key)
    return templates.TemplateResponse(
        request,
        "ordering_orders.html",
        {
            "title": "Đơn của tôi",
            "demo_customer": DEMO_CUSTOMER_EMAIL,
            "orders": views,
            "total": total,
            **_flash(request),
        },
    )


@router.get("/orders/{order_code}")
async def order_detail(request: Request, db: DbSession, order_code: str):
    account_key = await adapters.get_account_key_by_email(db, DEMO_CUSTOMER_EMAIL)
    try:
        view = await service.get_customer_order(
            db, account_key=account_key, order_code=order_code.upper()
        )
        invoice = None
        try:
            invoice = await service.get_invoice_for_customer(
                db, account_key=account_key, order_code=view.order_code
            )
        except OrderingError:
            invoice = None
    except OrderingError as exc:
        return _redirect("/dev/ordering/orders", error=exc.message)

    return templates.TemplateResponse(
        request,
        "ordering_order_detail.html",
        {
            "title": f"Đơn {view.order_code}",
            "demo_customer": DEMO_CUSTOMER_EMAIL,
            "order": view,
            "invoice": invoice,
            **_flash(request),
        },
    )


@router.post("/orders/{order_code}/cancel")
async def order_cancel_customer(db: DbSession, order_code: str):
    try:
        account_key = await adapters.get_account_key_by_email(db, DEMO_CUSTOMER_EMAIL)
        await service.cancel_order_by_customer(
            db,
            account_key=account_key,
            order_code=order_code.upper(),
            inventory=adapters.DbInventoryGateway(db),
        )
        return _redirect(
            f"/dev/ordering/orders/{order_code.upper()}",
            ok="Đã hủy đơn",
        )
    except OrderingError as exc:
        return _redirect(
            f"/dev/ordering/orders/{order_code.upper()}",
            error=exc.message,
        )


@router.get("/orders/{order_code}/invoice")
async def order_invoice_customer(request: Request, db: DbSession, order_code: str):
    account_key = await adapters.get_account_key_by_email(db, DEMO_CUSTOMER_EMAIL)
    try:
        invoice = await service.get_invoice_for_customer(
            db, account_key=account_key, order_code=order_code.upper()
        )
    except OrderingError as exc:
        return _redirect(
            f"/dev/ordering/orders/{order_code.upper()}",
            error=exc.message,
        )
    return templates.TemplateResponse(
        request,
        "ordering_invoice.html",
        {
            "title": f"Hóa đơn {invoice.invoice_id}",
            "demo_customer": DEMO_CUSTOMER_EMAIL,
            "demo_employee": None,
            "invoice": invoice,
            "staff_mode": False,
            **_flash(request),
        },
    )


@router.get("/staff")
async def staff_page(request: Request):
    return templates.TemplateResponse(
        request,
        "ordering_staff.html",
        {
            "title": "NV — ordering",
            "demo_employee": DEMO_EMPLOYEE_EMAIL,
            **_flash(request),
        },
    )


@router.post("/staff/confirm")
async def staff_confirm(
    db: DbSession,
    order_code: Annotated[str, Form()],
):
    try:
        employee = await adapters.get_account_key_by_email(db, DEMO_EMPLOYEE_EMAIL)
        order = await service.confirm_order(
            db, employee_key=employee, order_code=order_code.strip().upper()
        )
        return _redirect(
            "/dev/ordering/staff",
            ok=f"Đã xác nhận {order.order_code}",
        )
    except OrderingError as exc:
        return _redirect("/dev/ordering/staff", error=exc.message)


@router.post("/staff/mark-paid")
async def staff_mark_paid(
    db: DbSession,
    order_code: Annotated[str, Form()],
):
    """Giả lập payment báo PAID (UC-25) để thử confirm QR / ẩn QR."""
    try:
        order = await service.mark_order_paid_by_code(db, order_code.strip().upper())
        # Chuyển sang chi tiết đơn để thấy payment_status đổi (order_status vẫn PENDING).
        return _redirect(
            f"/dev/ordering/orders/{order.order_code}",
            ok=(
                f"Đã PAID {order.order_code}. "
                "Trạng thái đơn vẫn PENDING — NV cần bấm Xác nhận (UC-23)."
            ),
        )
    except OrderingError as exc:
        return _redirect("/dev/ordering/staff", error=exc.message)


@router.post("/staff/cancel")
async def staff_cancel(
    db: DbSession,
    order_code: Annotated[str, Form()],
    reason: Annotated[str, Form()],
):
    try:
        employee = await adapters.get_account_key_by_email(db, DEMO_EMPLOYEE_EMAIL)
        order = await service.cancel_order_by_employee(
            db,
            employee_key=employee,
            order_code=order_code.strip().upper(),
            reason=reason,
            inventory=adapters.DbInventoryGateway(db),
        )
        return _redirect(
            "/dev/ordering/staff",
            ok=f"NV đã hủy {order.order_code}",
        )
    except OrderingError as exc:
        return _redirect("/dev/ordering/staff", error=exc.message)


@router.post("/staff/transition")
async def staff_transition(
    db: DbSession,
    order_code: Annotated[str, Form()],
    to_status: Annotated[str, Form()],
):
    try:
        order = await service.transition_status_for_shipping(
            db,
            order_code=order_code.strip().upper(),
            to_status=to_status.strip().upper(),
            source="EMPLOYEE",
        )
        return _redirect(
            "/dev/ordering/staff",
            ok=f"{order.order_code} → {order.order_status}",
        )
    except OrderingError as exc:
        return _redirect("/dev/ordering/staff", error=exc.message)


@router.post("/staff/auto-cancel")
async def staff_auto_cancel():
    cancelled = await jobs.run_auto_cancel_overdue_qr()
    if cancelled:
        return _redirect(
            "/dev/ordering/staff",
            ok=f"UC-24 hủy: {', '.join(cancelled)}",
        )
    return _redirect("/dev/ordering/staff", ok="UC-24: không có đơn quá hạn")


@router.get("/staff/invoice/{invoice_id}")
async def staff_invoice(request: Request, db: DbSession, invoice_id: str):
    try:
        invoice = await service.get_invoice_for_staff(db, invoice_id.strip())
    except OrderingError as exc:
        return _redirect("/dev/ordering/staff", error=exc.message)
    return templates.TemplateResponse(
        request,
        "ordering_invoice.html",
        {
            "title": f"Hóa đơn {invoice.invoice_id}",
            "demo_customer": None,
            "demo_employee": DEMO_EMPLOYEE_EMAIL,
            "invoice": invoice,
            "staff_mode": True,
            **_flash(request),
        },
    )


@router.post("/staff/lookup-invoice")
async def staff_lookup_invoice(invoice_id: Annotated[str, Form()]):
    return _redirect(f"/dev/ordering/staff/invoice/{invoice_id.strip()}")
