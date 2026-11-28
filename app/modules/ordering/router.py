"""Tầng Route ordering — UI thử SSR (/dev/ordering).

Router chỉ validate input / gọi service / render Jinja. Không gọi repository.
Adapter tạm [GD]: identity demo + DbInventory/DbCatalog đến khi teammate sẵn service.
Sổ địa chỉ: gọi identity.service công khai (UC-41).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from decimal import Decimal, InvalidOperation
from typing import Annotated
from urllib.parse import urlencode
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.identity import service as identity_service
from app.modules.identity.exceptions import IdentityError
from app.modules.identity.schemas import ShippingAddressCreate, ShippingAddressView
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


def _shipping_from_address(addr: ShippingAddressView) -> ShippingInfo:
    return ShippingInfo(
        name=addr.name,
        phone=addr.phone,
        house_number=addr.house_number,
        ward=addr.ward,
        city=addr.city,
        country=addr.country,
    )


async def _selected_shipping_address(
    db: AsyncSession,
    *,
    account_key: UUID,
    selected_raw: str | None,
) -> ShippingAddressView | None:
    addresses = await identity_service.list_shipping_addresses(db, account_key)
    if not addresses:
        return None
    if selected_raw:
        try:
            key = UUID(selected_raw)
        except ValueError:
            key = None
        if key is not None:
            for addr in addresses:
                if addr.shipping_address_key == key:
                    return addr
    for addr in addresses:
        if addr.is_default:
            return addr
    return addresses[0]


def _parse_expected_total(raw: str | None) -> Decimal | None:
    if raw is None or not str(raw).strip():
        return None
    try:
        return Decimal(str(raw).strip())
    except InvalidOperation:
        return None


@router.get("")
async def ordering_home(request: Request, db: DbSession):
    # Ảnh hero từ seed catalog (adapter shopping tạm) — [GD]
    from app.modules.shopping import adapters as shopping_adapters

    products = await shopping_adapters.list_seed_products(db)
    hero = next((p for p in products if p.get("image_url")), products[0] if products else None)
    return templates.TemplateResponse(
        request,
        "ordering_home.html",
        {
            "title": "Thử ordering",
            "demo_customer": DEMO_CUSTOMER_EMAIL,
            "demo_employee": DEMO_EMPLOYEE_EMAIL,
            "hero": hero,
            "nav_active": "home",
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

    addresses = await identity_service.list_shipping_addresses(db, account_key)
    selected = await _selected_shipping_address(
        db,
        account_key=account_key,
        selected_raw=request.query_params.get("selected"),
    )
    address_view = request.query_params.get("view") or ""
    if address_view not in {"", "list", "add"}:
        address_view = ""
    if not addresses and address_view != "add":
        address_view = "add"

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
            "addresses": addresses,
            "selected_address": selected,
            "address_view": address_view,
            "nav_active": "checkout",
            **_flash(request),
        },
    )


@router.post("/checkout/addresses")
async def checkout_add_address(
    db: DbSession,
    name: Annotated[str, Form()],
    phone: Annotated[str, Form()],
    house_number: Annotated[str, Form()],
    ward: Annotated[str, Form()],
    city: Annotated[str, Form()],
    country: Annotated[str, Form()] = "Việt Nam",
):
    """UC-41 / UC-19: thêm địa chỉ tại checkout → lưu sổ, chọn cho đơn đang đặt."""
    try:
        account_key = await adapters.get_account_key_by_email(db, DEMO_CUSTOMER_EMAIL)
        created = await identity_service.add_shipping_address(
            db,
            account_key=account_key,
            data=ShippingAddressCreate(
                name=name,
                phone=phone,
                house_number=house_number,
                ward=ward,
                city=city,
                country=country,
            ),
        )
        return _redirect(
            "/dev/ordering/checkout",
            ok="Đã thêm địa chỉ vào sổ",
            selected=str(created.shipping_address_key),
        )
    except IdentityError as exc:
        return _redirect("/dev/ordering/checkout", error=exc.message, view="add")


@router.post("/checkout/addresses/default")
async def checkout_set_default_address(
    db: DbSession,
    address_key: Annotated[str, Form()],
):
    try:
        account_key = await adapters.get_account_key_by_email(db, DEMO_CUSTOMER_EMAIL)
        updated = await identity_service.set_default_shipping_address(
            db,
            account_key=account_key,
            address_key=UUID(address_key.strip()),
        )
        return _redirect(
            "/dev/ordering/checkout",
            ok="Đã đặt địa chỉ mặc định",
            selected=str(updated.shipping_address_key),
            view="list",
        )
    except (IdentityError, ValueError) as exc:
        msg = getattr(exc, "message", "Địa chỉ không hợp lệ")
        return _redirect("/dev/ordering/checkout", error=msg, view="list")


@router.post("/checkout/cod")
async def checkout_cod(
    db: DbSession,
    shipping_address_key: Annotated[str, Form()],
    expected_total: Annotated[str | None, Form()] = None,
):
    try:
        account_key = await adapters.get_account_key_by_email(db, DEMO_CUSTOMER_EMAIL)
        addr = await identity_service.get_shipping_address(
            db,
            account_key=account_key,
            address_key=UUID(shipping_address_key.strip()),
        )
        order = await service.place_cod_order(
            db,
            account_key=account_key,
            shipping=_shipping_from_address(addr),
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
            selected=shipping_address_key.strip(),
        )
    except (OrderingError, IdentityError, ValueError) as exc:
        msg = getattr(exc, "message", "Thiếu hoặc không hợp lệ địa chỉ giao hàng")
        return _redirect(
            "/dev/ordering/checkout",
            error=msg,
            selected=shipping_address_key.strip() if shipping_address_key else "",
        )


@router.post("/checkout/qr")
async def checkout_qr(
    db: DbSession,
    shipping_address_key: Annotated[str, Form()],
    expected_total: Annotated[str | None, Form()] = None,
):
    try:
        account_key = await adapters.get_account_key_by_email(db, DEMO_CUSTOMER_EMAIL)
        addr = await identity_service.get_shipping_address(
            db,
            account_key=account_key,
            address_key=UUID(shipping_address_key.strip()),
        )
        order = await service.place_qr_order(
            db,
            account_key=account_key,
            shipping=_shipping_from_address(addr),
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
            selected=shipping_address_key.strip(),
        )
    except (OrderingError, IdentityError, ValueError) as exc:
        msg = getattr(exc, "message", "Thiếu hoặc không hợp lệ địa chỉ giao hàng")
        return _redirect(
            "/dev/ordering/checkout",
            error=msg,
            selected=shipping_address_key.strip() if shipping_address_key else "",
        )


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
            "nav_active": "orders",
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
            "staff_mode": False,
            "nav_active": "orders",
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
            "nav_active": "orders",
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
            "nav_active": "staff",
            **_flash(request),
        },
    )


@router.post("/staff/lookup-order")
async def staff_lookup_order(order_code: Annotated[str, Form()]):
    return _redirect(f"/dev/ordering/staff/orders/{order_code.strip().upper()}")


@router.get("/staff/orders/{order_code}")
async def staff_order_detail(request: Request, db: DbSession, order_code: str):
    try:
        view = await service.get_staff_order(db, order_code=order_code.upper())
    except OrderingError as exc:
        return _redirect("/dev/ordering/staff", error=exc.message)
    return templates.TemplateResponse(
        request,
        "ordering_order_detail.html",
        {
            "title": f"NV · Đơn {view.order_code}",
            "demo_employee": DEMO_EMPLOYEE_EMAIL,
            "order": view,
            "invoice": None,
            "staff_mode": True,
            "nav_active": "staff",
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
            "nav_active": "staff",
            **_flash(request),
        },
    )


@router.post("/staff/lookup-invoice")
async def staff_lookup_invoice(invoice_id: Annotated[str, Form()]):
    return _redirect(f"/dev/ordering/staff/invoice/{invoice_id.strip()}")
