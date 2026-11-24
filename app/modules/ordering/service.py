"""Service ordering — nghiệp vụ đặt hàng / vòng đời / hóa đơn."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from app.modules.ordering import repository
from app.modules.ordering.dependencies import (
    AppliedPromotion,
    CatalogPricing,
    InventoryGateway,
    NoPromotionGateway,
    PromotionGateway,
)
from app.modules.ordering.exceptions import (
    CancelNotAllowedError,
    EmptyCartError,
    InsufficientStockError,
    InvalidCancelReasonError,
    InvalidOrderStateError,
    MissingShippingInfoError,
    OrderNotFoundError,
    PriceChangedError,
    UnpaidQrConfirmError,
)
from app.modules.ordering.models import Order, OrderDetail
from app.modules.ordering.schemas import (
    InvoiceView,
    OrderLineQuote,
    OrderQuote,
    OrderView,
    ShippingInfo,
)
from app.modules.shopping import service as shopping_service
from app.shared.config.settings import Config
from app.shared.database.transaction import transaction
from app.shared.money import line_amount, to_vnd

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_QR_PAYMENT_HOURS = 24
_CUSTOMER_CANCEL_STATUSES = frozenset({"PENDING"})
_EMPLOYEE_CANCEL_STATUSES = frozenset({"PENDING", "CONFIRMED", "AWAITING_PICKUP"})


def _shipping_fee() -> Decimal:
    return to_vnd(Decimal(str(Config.SHIPPING_FEE)))


def _new_order_code() -> str:
    return "".join(secrets.choice(_CROCKFORD) for _ in range(8))


def _validate_shipping(info: ShippingInfo) -> None:
    checks = {
        "name": info.name,
        "phone": info.phone,
        "house_number": info.house_number,
        "ward": info.ward,
        "city": info.city,
        "country": info.country,
    }
    for field, value in checks.items():
        if not value or not str(value).strip():
            raise MissingShippingInfoError(field)


async def _unique_order_code(db: AsyncSession) -> str:
    for _ in range(20):
        code = _new_order_code()
        if not await repository.order_code_exists(db, code):
            return code
    raise RuntimeError("Không sinh được order_code duy nhất")


async def build_quote(
    db: AsyncSession,
    *,
    account_key: UUID,
    inventory: InventoryGateway,
    pricing: CatalogPricing,
    promotion: PromotionGateway | None = None,
    voucher_code: str | None = None,
) -> OrderQuote:
    """Tính tạm tính / giảm / phí / tổng từ giỏ hiện tại (không ghi DB)."""
    promo = promotion or NoPromotionGateway()
    cart = await shopping_service.list_cart_variant_quantities(db, account_key)
    lines: list[OrderLineQuote] = []
    for variant_key, quantity in cart.items():
        stock = await inventory.get_stock_quantity(variant_key)
        if stock <= 0:
            continue
        if quantity > stock:
            raise InsufficientStockError(str(variant_key))
        unit = to_vnd(await pricing.get_unit_price(variant_key))
        cost = to_vnd(await inventory.get_cost_price(variant_key))
        lines.append(
            OrderLineQuote(
                variant_key=variant_key,
                quantity=quantity,
                unit_price=unit,
                line_total=line_amount(unit, quantity),
                cost_price=cost,
            )
        )
    if not lines:
        raise EmptyCartError()

    subtotal = to_vnd(sum((ln.line_total for ln in lines), Decimal("0")))
    applied = await promo.quote(subtotal=subtotal, voucher_code=voucher_code)
    discount = to_vnd(applied.discount_amount)
    if discount > subtotal:
        discount = subtotal
    shipping = _shipping_fee()
    total = to_vnd(subtotal - discount + shipping)
    return OrderQuote(
        lines=tuple(lines),
        subtotal=subtotal,
        discount_amount=discount,
        shipping_fee=shipping,
        total_price=total,
        order_promotion_key=applied.order_promotion_key,
        code_promotion_key=applied.code_promotion_key,
    )


async def _place_order(
    db: AsyncSession,
    *,
    account_key: UUID,
    payment_name: str,
    shipping: ShippingInfo,
    inventory: InventoryGateway,
    pricing: CatalogPricing,
    promotion: PromotionGateway | None = None,
    voucher_code: str | None = None,
    expected_total: Decimal | None = None,
) -> Order:
    _validate_shipping(shipping)
    promo = promotion or NoPromotionGateway()

    async with transaction(db):
        quote = await build_quote(
            db,
            account_key=account_key,
            inventory=inventory,
            pricing=pricing,
            promotion=promo,
            voucher_code=voucher_code,
        )
        if expected_total is not None and to_vnd(expected_total) != quote.total_price:
            raise PriceChangedError(quote.total_price)

        for line in quote.lines:
            try:
                await inventory.deduct_stock(line.variant_key, line.quantity)
            except InsufficientStockError:
                raise
            except Exception as exc:
                raise InsufficientStockError(str(line.variant_key)) from exc

        applied = AppliedPromotion(
            discount_amount=quote.discount_amount,
            order_promotion_key=quote.order_promotion_key,
            code_promotion_key=quote.code_promotion_key,
        )
        await promo.consume(applied)

        payment_key = await repository.get_payment_key(db, payment_name)
        order_code = await _unique_order_code(db)
        order = Order(
            order_code=order_code,
            order_account_key=account_key,
            order_payment_key=payment_key,
            order_order_promotion_key=quote.order_promotion_key,
            order_code_promotion_key=quote.code_promotion_key,
            order_customer_name=shipping.name.strip(),
            order_customer_phone_number=shipping.phone.strip(),
            order_customer_house_number=shipping.house_number.strip(),
            order_customer_ward=shipping.ward.strip(),
            order_customer_city=shipping.city.strip(),
            order_customer_country=shipping.country.strip(),
            order_discount_amount=quote.discount_amount,
            order_shipping_fee=quote.shipping_fee,
            order_total_price=quote.total_price,
            order_payment_status="UNPAID",
            order_status="PENDING",
        )
        await repository.create_order(db, order)

        for line in quote.lines:
            await repository.add_order_detail(
                db,
                OrderDetail(
                    order_detail_order_key=order.order_key,
                    order_detail_variant_key=line.variant_key,
                    order_detail_quantity=line.quantity,
                    order_detail_unit_price=line.unit_price,
                    order_detail_product_promotion_key=line.product_promotion_key,
                    order_detail_cost_price=line.cost_price,
                ),
            )

        await repository.add_status_history(
            db,
            order_key=order.order_key,
            from_value=None,
            to_value="PENDING",
            source="CUSTOMER",
            changed_by=account_key,
        )

        await shopping_service.remove_ordered_variants(
            db,
            account_key,
            [line.variant_key for line in quote.lines],
        )
        order_key = order.order_key

    loaded = await repository.get_order_by_key(db, order_key)
    assert loaded is not None
    return loaded


async def place_cod_order(
    db: AsyncSession,
    *,
    account_key: UUID,
    shipping: ShippingInfo,
    inventory: InventoryGateway,
    pricing: CatalogPricing,
    promotion: PromotionGateway | None = None,
    voucher_code: str | None = None,
    expected_total: Decimal | None = None,
) -> Order:
    """UC-19: đặt hàng COD."""
    return await _place_order(
        db,
        account_key=account_key,
        payment_name="COD",
        shipping=shipping,
        inventory=inventory,
        pricing=pricing,
        promotion=promotion,
        voucher_code=voucher_code,
        expected_total=expected_total,
    )


async def place_qr_order(
    db: AsyncSession,
    *,
    account_key: UUID,
    shipping: ShippingInfo,
    inventory: InventoryGateway,
    pricing: CatalogPricing,
    promotion: PromotionGateway | None = None,
    voucher_code: str | None = None,
    expected_total: Decimal | None = None,
) -> Order:
    """UC-20: đặt hàng QR (UNPAID; hạn = created + 24h)."""
    return await _place_order(
        db,
        account_key=account_key,
        payment_name="QR",
        shipping=shipping,
        inventory=inventory,
        pricing=pricing,
        promotion=promotion,
        voucher_code=voucher_code,
        expected_total=expected_total,
    )


def _payment_deadline(order: Order, payment_name: str) -> datetime | None:
    if payment_name != "QR" or order.order_created_date is None:
        return None
    created = order.order_created_date
    if created.tzinfo is None:
        created = created.replace(tzinfo=UTC)
    return created + timedelta(hours=_QR_PAYMENT_HOURS)


def _show_qr(order: Order, payment_name: str, now: datetime | None = None) -> bool:
    if payment_name != "QR":
        return False
    if order.order_status == "CANCELLED":
        return False
    if order.order_payment_status == "PAID":
        return False
    deadline = _payment_deadline(order, payment_name)
    if deadline is None:
        return False
    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return current < deadline


async def to_order_view(db: AsyncSession, order: Order) -> OrderView:
    payment_name = await repository.payment_name_of(db, order.order_payment_key)
    created = order.order_created_date or datetime.now(UTC)
    if created.tzinfo is None:
        created = created.replace(tzinfo=UTC)
    show = _show_qr(order, payment_name)
    return OrderView(
        order_key=order.order_key,
        order_code=order.order_code,
        account_key=order.order_account_key,
        payment_name=payment_name,
        status=order.order_status,
        payment_status=order.order_payment_status,
        discount_amount=to_vnd(order.order_discount_amount),
        shipping_fee=to_vnd(order.order_shipping_fee),
        total_price=to_vnd(order.order_total_price),
        customer_name=order.order_customer_name,
        customer_phone=order.order_customer_phone_number,
        created_at=created,
        payment_deadline=_payment_deadline(order, payment_name),
        show_qr=show,
        transfer_content=f"SOBIE{order.order_code}" if show else None,
    )


async def list_customer_orders(
    db: AsyncSession, account_key: UUID, *, page: int = 1, page_size: int = 12
) -> tuple[list[OrderView], int]:
    if page < 1:
        page = 1
    offset = (page - 1) * page_size
    total = await repository.count_orders_for_account(db, account_key)
    orders = await repository.list_orders_for_account(
        db, account_key, limit=page_size, offset=offset
    )
    views = [await to_order_view(db, o) for o in orders]
    return views, total


async def get_customer_order(
    db: AsyncSession, *, account_key: UUID, order_code: str
) -> OrderView:
    order = await repository.get_order_by_code(db, order_code)
    if order is None or order.order_account_key != account_key:
        raise OrderNotFoundError()
    return await to_order_view(db, order)


async def cancel_order_by_customer(
    db: AsyncSession,
    *,
    account_key: UUID,
    order_code: str,
    inventory: InventoryGateway,
    promotion: PromotionGateway | None = None,
) -> Order:
    promo = promotion or NoPromotionGateway()
    async with transaction(db):
        order = await repository.get_order_by_code(db, order_code)
        if order is None or order.order_account_key != account_key:
            raise OrderNotFoundError()
        if order.order_status not in _CUSTOMER_CANCEL_STATUSES:
            raise CancelNotAllowedError()
        await _cancel_order(
            db,
            order=order,
            source="CUSTOMER",
            changed_by=account_key,
            note=None,
            inventory=inventory,
            promotion=promo,
        )
        order_key = order.order_key

    loaded = await repository.get_order_by_key(db, order_key)
    assert loaded is not None
    return loaded


async def cancel_order_by_employee(
    db: AsyncSession,
    *,
    employee_key: UUID,
    order_code: str,
    reason: str,
    inventory: InventoryGateway,
    promotion: PromotionGateway | None = None,
) -> Order:
    if not reason or not reason.strip() or len(reason) > 500:
        raise InvalidCancelReasonError()
    promo = promotion or NoPromotionGateway()
    async with transaction(db):
        order = await repository.get_order_by_code(db, order_code)
        if order is None:
            raise OrderNotFoundError()
        if order.order_status not in _EMPLOYEE_CANCEL_STATUSES:
            raise CancelNotAllowedError()
        await _cancel_order(
            db,
            order=order,
            source="EMPLOYEE",
            changed_by=employee_key,
            note=reason.strip(),
            inventory=inventory,
            promotion=promo,
        )
        order_key = order.order_key

    loaded = await repository.get_order_by_key(db, order_key)
    assert loaded is not None
    return loaded


async def _cancel_order(
    db: AsyncSession,
    *,
    order: Order,
    source: str,
    changed_by: UUID | None,
    note: str | None,
    inventory: InventoryGateway,
    promotion: PromotionGateway,
) -> Order:
    if order.order_status == "CANCELLED":
        raise CancelNotAllowedError("Đơn đã hủy")
    from_status = order.order_status
    details = await repository.list_order_details(db, order.order_key)
    for d in details:
        await inventory.restore_stock(d.order_detail_variant_key, d.order_detail_quantity)

    applied = AppliedPromotion(
        discount_amount=to_vnd(order.order_discount_amount),
        order_promotion_key=order.order_order_promotion_key,
        code_promotion_key=order.order_code_promotion_key,
    )
    await promotion.restore(applied)

    order.order_status = "CANCELLED"
    await repository.save_order(db, order)
    await repository.add_status_history(
        db,
        order_key=order.order_key,
        from_value=from_status,
        to_value="CANCELLED",
        source=source,
        changed_by=changed_by,
        note=note,
    )
    order_key = order.order_key
    # Caller đang trong transaction; trả object hiện tại (flush rồi).
    return order


async def confirm_order(
    db: AsyncSession,
    *,
    employee_key: UUID,
    order_code: str,
) -> Order:
    """UC-23: NV xác nhận; QR phải PAID."""
    async with transaction(db):
        order = await repository.get_order_by_code(db, order_code)
        if order is None:
            raise OrderNotFoundError()
        if order.order_status != "PENDING":
            raise InvalidOrderStateError(f"Đơn đang ở trạng thái {order.order_status}")
        payment_name = await repository.payment_name_of(db, order.order_payment_key)
        if payment_name == "QR" and order.order_payment_status != "PAID":
            raise UnpaidQrConfirmError()
        order.order_status = "CONFIRMED"
        await repository.save_order(db, order)
        await repository.add_status_history(
            db,
            order_key=order.order_key,
            from_value="PENDING",
            to_value="CONFIRMED",
            source="EMPLOYEE",
            changed_by=employee_key,
        )
        order_key = order.order_key

    loaded = await repository.get_order_by_key(db, order_key)
    assert loaded is not None
    return loaded


async def mark_order_paid_by_code(db: AsyncSession, order_code: str) -> Order:
    """Service công khai cho payment (UC-25): chỉ đơn QR PENDING + UNPAID còn hạn."""
    async with transaction(db):
        order = await repository.get_order_by_code(db, order_code)
        if order is None:
            raise OrderNotFoundError()
        payment_name = await repository.payment_name_of(db, order.order_payment_key)
        if payment_name != "QR":
            raise InvalidOrderStateError("Chỉ đối soát thanh toán cho đơn chuyển khoản QR")
        if order.order_status != "PENDING":
            raise InvalidOrderStateError(
                f"Đơn đang ở trạng thái {order.order_status}, không đối soát được"
            )
        if order.order_payment_status != "UNPAID":
            raise InvalidOrderStateError("Đơn đã thanh toán hoặc không còn UNPAID")
        deadline = _payment_deadline(order, payment_name)
        now = datetime.now(UTC)
        if deadline is not None and now >= deadline:
            raise InvalidOrderStateError("Đơn QR đã quá hạn thanh toán")
        order.order_payment_status = "PAID"
        await repository.save_order(db, order)
        order_key = order.order_key

    loaded = await repository.get_order_by_key(db, order_key)
    assert loaded is not None
    return loaded


async def transition_status_for_shipping(
    db: AsyncSession,
    *,
    order_code: str,
    to_status: str,
    source: str = "SHIPPING_SIMULATOR",
) -> Order:
    """Service công khai cho shipping (UC-36 / UC-40)."""
    allowed = {
        "CONFIRMED": {"AWAITING_PICKUP"},
        "AWAITING_PICKUP": {"SHIPPING"},
        "SHIPPING": {"DELIVERED", "DELIVERY_FAILED"},
    }
    async with transaction(db):
        order = await repository.get_order_by_code(db, order_code)
        if order is None:
            raise OrderNotFoundError()
        ok = allowed.get(order.order_status, frozenset())
        if to_status not in ok:
            raise InvalidOrderStateError()
        from_status = order.order_status
        order.order_status = to_status
        if to_status == "DELIVERED":
            payment_name = await repository.payment_name_of(db, order.order_payment_key)
            if payment_name == "COD":
                order.order_payment_status = "PAID"
        await repository.save_order(db, order)
        await repository.add_status_history(
            db,
            order_key=order.order_key,
            from_value=from_status,
            to_value=to_status,
            source=source,
        )
        if to_status == "DELIVERED":
            await _issue_invoice_unlocked(db, order)
        order_key = order.order_key

    loaded = await repository.get_order_by_key(db, order_key)
    assert loaded is not None
    return loaded


async def auto_cancel_overdue_qr_orders(
    db: AsyncSession,
    *,
    inventory: InventoryGateway,
    promotion: PromotionGateway | None = None,
    now: datetime | None = None,
) -> list[str]:
    """UC-24: hủy QR quá 24h chưa thanh toán. Trả danh sách order_code đã hủy."""
    promo = promotion or NoPromotionGateway()
    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    cutoff = current - timedelta(hours=_QR_PAYMENT_HOURS)
    cancelled: list[str] = []
    overdue = await repository.list_overdue_unpaid_qr_orders(db, older_than=cutoff)
    for order in overdue:
        try:
            async with transaction(db):
                fresh = await repository.get_order_by_key(db, order.order_key)
                if fresh is None:
                    continue
                if (
                    fresh.order_status != "PENDING"
                    or fresh.order_payment_status != "UNPAID"
                ):
                    continue
                code = fresh.order_code
                await _cancel_order(
                    db,
                    order=fresh,
                    source="SYSTEM",
                    changed_by=None,
                    note="Quá hạn thanh toán",
                    inventory=inventory,
                    promotion=promo,
                )
                cancelled.append(code)
        except Exception:
            continue
    return cancelled


async def _issue_invoice_unlocked(db: AsyncSession, order: Order) -> InvoiceView | None:
    existing = await repository.get_invoice_by_order(db, order.order_key)
    if existing is not None:
        return InvoiceView(
            invoice_id=existing.invoice_id,
            order_code=order.order_code,
            created_at=existing.invoice_created_date or datetime.now(UTC),
            snapshot=dict(existing.invoice_snapshot_json),
        )
    payment_name = await repository.payment_name_of(db, order.order_payment_key)
    details = await repository.list_order_details(db, order.order_key)
    snapshot = {
        "order_code": order.order_code,
        "payment_method": payment_name,
        "customer_name": order.order_customer_name,
        "customer_phone": order.order_customer_phone_number,
        "address": {
            "house_number": order.order_customer_house_number,
            "ward": order.order_customer_ward,
            "city": order.order_customer_city,
            "country": order.order_customer_country,
        },
        "discount_amount": str(to_vnd(order.order_discount_amount)),
        "shipping_fee": str(to_vnd(order.order_shipping_fee)),
        "total_price": str(to_vnd(order.order_total_price)),
        "lines": [
            {
                "variant_key": str(d.order_detail_variant_key),
                "quantity": d.order_detail_quantity,
                "unit_price": str(to_vnd(d.order_detail_unit_price)),
            }
            for d in details
        ],
    }
    invoice_id = f"HD-{order.order_code}"
    inv = await repository.create_invoice(
        db, invoice_id=invoice_id, order_key=order.order_key, snapshot=snapshot
    )
    return InvoiceView(
        invoice_id=inv.invoice_id,
        order_code=order.order_code,
        created_at=inv.invoice_created_date or datetime.now(UTC),
        snapshot=snapshot,
    )


async def issue_invoice_for_delivered(
    db: AsyncSession, order_code: str
) -> InvoiceView:
    """UC-26: gọi khi đơn DELIVERED (idempotent)."""
    async with transaction(db):
        order = await repository.get_order_by_code(db, order_code)
        if order is None:
            raise OrderNotFoundError()
        if order.order_status != "DELIVERED":
            raise InvalidOrderStateError("Chỉ xuất hóa đơn khi giao thành công")
        payment_name = await repository.payment_name_of(db, order.order_payment_key)
        if payment_name == "COD" and order.order_payment_status != "PAID":
            order.order_payment_status = "PAID"
            await repository.save_order(db, order)
        view = await _issue_invoice_unlocked(db, order)
        assert view is not None
        return view


async def get_invoice_for_customer(
    db: AsyncSession, *, account_key: UUID, order_code: str
) -> InvoiceView:
    order = await repository.get_order_by_code(db, order_code)
    if order is None or order.order_account_key != account_key:
        raise OrderNotFoundError()
    inv = await repository.get_invoice_by_order(db, order.order_key)
    if inv is None:
        raise OrderNotFoundError()
    return InvoiceView(
        invoice_id=inv.invoice_id,
        order_code=order.order_code,
        created_at=inv.invoice_created_date or datetime.now(UTC),
        snapshot=dict(inv.invoice_snapshot_json),
    )


async def get_invoice_for_staff(db: AsyncSession, invoice_id: str) -> InvoiceView:
    inv = await repository.get_invoice_by_id(db, invoice_id)
    if inv is None:
        raise OrderNotFoundError()
    order = await repository.get_order_by_key(db, inv.invoice_order_key)
    if order is None:
        raise OrderNotFoundError()
    return InvoiceView(
        invoice_id=inv.invoice_id,
        order_code=order.order_code,
        created_at=inv.invoice_created_date or datetime.now(UTC),
        snapshot=dict(inv.invoice_snapshot_json),
    )
