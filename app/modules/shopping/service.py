"""Tầng Service của module shopping: nghiệp vụ và điều phối transaction.

Service công khai cho module khác:
- create_customer_containers: tạo giỏ + wishlist trống (identity UC-01/UC-06).
- list_cart_variant_quantities / remove_ordered_variants: cho ordering khi đặt hàng.

Chỉ gọi repository của chính module này; tồn kho / giá / sản phẩm lấy qua protocol
(catalog, inventory) do caller inject.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from app.modules.shopping import repository
from app.modules.shopping.dependencies import (
    ProductCatalog,
    VariantAvailability,
    VariantPricing,
)
from app.modules.shopping.exceptions import (
    CartItemNotFoundError,
    CartNotFoundError,
    InsufficientStockError,
    InvalidQuantityError,
    MergeRequestConflictError,
    ProductNotFoundError,
    ShoppingError,
    WishlistNotFoundError,
)
from app.modules.shopping.schemas import (
    CartLineView,
    CartView,
    GuestCartLine,
    WishlistItemView,
    WishlistView,
)
from app.shared.database.transaction import transaction
from app.shared.money import line_amount, to_vnd

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession

_DEFAULT_WISHLIST_PAGE_SIZE = 12  # [GD] khớp gợi ý phân trang catalog UC-10


def _require_positive_int_quantity(quantity: int) -> None:
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        raise InvalidQuantityError()


def _merge_payload_hash(lines: list[GuestCartLine]) -> str:
    normalized = sorted(
        (
            {"variant_key": str(line.variant_key), "quantity": line.quantity}
            for line in lines
        ),
        key=lambda item: item["variant_key"],
    )
    raw = json.dumps(normalized, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def create_customer_containers(db: AsyncSession, account_key: UUID) -> None:
    """Tạo 1 giỏ và 1 wishlist trống cho tài khoản Khách hàng (cùng transaction của identity)."""
    await repository.create_cart(db, account_key)
    await repository.create_wishlist(db, account_key)


async def list_cart_variant_quantities(
    db: AsyncSession, account_key: UUID
) -> dict[UUID, int]:
    """Đọc các dòng giỏ (cho ordering)."""
    cart_key = await repository.get_cart_key(db, account_key)
    if cart_key is None:
        raise CartNotFoundError()
    items = await repository.list_cart_items(db, cart_key)
    return {variant_key: qty for _, variant_key, qty in items}


async def remove_ordered_variants(
    db: AsyncSession, account_key: UUID, variant_keys: list[UUID]
) -> None:
    """Xóa các dòng đã đặt khỏi giỏ (cho ordering, cùng transaction tạo đơn)."""
    cart_key = await repository.get_cart_key(db, account_key)
    if cart_key is None:
        raise CartNotFoundError()
    await repository.delete_cart_items_by_variants(db, cart_key, variant_keys)


async def add_item_to_cart(
    db: AsyncSession,
    *,
    account_key: UUID,
    variant_key: UUID,
    quantity: int,
    availability: VariantAvailability,
) -> int:
    """UC-18 AC-1 / AC-2: thêm hoặc cộng dồn; không vượt tồn; không trừ tồn."""
    _require_positive_int_quantity(quantity)

    async with transaction(db):
        cart_key = await repository.get_cart_key(db, account_key)
        if cart_key is None:
            raise CartNotFoundError()

        stock = await availability.get_stock_quantity(variant_key)
        existing = await repository.get_cart_item_quantity(db, cart_key, variant_key)
        current_qty = existing[1] if existing else 0
        new_qty = current_qty + quantity
        if new_qty > stock:
            raise InsufficientStockError(stock)

        if existing is None:
            return await repository.insert_cart_item(
                db, cart_key, variant_key, new_qty
            )
        return await repository.update_cart_item_quantity(db, existing[0], new_qty)


async def set_cart_item_quantity(
    db: AsyncSession,
    *,
    account_key: UUID,
    variant_key: UUID,
    quantity: int,
    availability: VariantAvailability,
) -> int:
    """UC-18 AC-3: đổi số lượng dòng; vượt tồn thì từ chối, giữ nguyên."""
    _require_positive_int_quantity(quantity)

    async with transaction(db):
        cart_key = await repository.get_cart_key(db, account_key)
        if cart_key is None:
            raise CartNotFoundError()

        existing = await repository.get_cart_item_quantity(db, cart_key, variant_key)
        if existing is None:
            raise CartItemNotFoundError()

        stock = await availability.get_stock_quantity(variant_key)
        if quantity > stock:
            raise InsufficientStockError(stock)

        return await repository.update_cart_item_quantity(db, existing[0], quantity)


async def remove_cart_item(
    db: AsyncSession, *, account_key: UUID, variant_key: UUID
) -> None:
    """UC-18 AC-4: xóa một dòng."""
    async with transaction(db):
        cart_key = await repository.get_cart_key(db, account_key)
        if cart_key is None:
            raise CartNotFoundError()
        deleted = await repository.delete_cart_item(db, cart_key, variant_key)
        if not deleted:
            raise CartItemNotFoundError()


async def get_cart(
    db: AsyncSession,
    *,
    account_key: UUID,
    availability: VariantAvailability,
    pricing: VariantPricing,
) -> CartView:
    """UC-18 AC-1/AC-7/AC-8: xem giỏ; giá hiện tại; dòng hết hàng/ngừng bán không vào tạm tính."""
    cart_key = await repository.get_cart_key(db, account_key)
    if cart_key is None:
        raise CartNotFoundError()

    rows = await repository.list_cart_items(db, cart_key)
    lines: list[CartLineView] = []
    subtotal = Decimal("0")

    for _, variant_key, quantity in rows:
        sellable = await availability.is_variant_sellable(variant_key)
        stock = await availability.get_stock_quantity(variant_key)
        unit_price = to_vnd(await pricing.get_current_unit_price(variant_key))

        if not sellable:
            reason = "Ngừng bán"
            available = False
        elif stock <= 0:
            reason = "Hết hàng"
            available = False
        else:
            reason = None
            available = True

        line_total = line_amount(unit_price, quantity) if available else Decimal("0")
        if available:
            subtotal += line_total

        lines.append(
            CartLineView(
                variant_key=variant_key,
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total,
                is_available=available,
                unavailable_reason=reason,
            )
        )

    return CartView(
        account_key=account_key,
        lines=tuple(lines),
        subtotal=to_vnd(subtotal),
    )


async def merge_guest_cart(
    db: AsyncSession,
    *,
    account_key: UUID,
    merge_id: str,
    guest_lines: list[GuestCartLine],
    availability: VariantAvailability,
) -> dict[UUID, int]:
    """UC-18 AC-6/9/10/11: gộp giỏ localStorage vào giỏ tài khoản (idempotent theo merge_id).

    Trả map variant_key → quantity sau gộp. Hiển thị giá: gọi get_cart sau đó.
    """
    if not merge_id or not str(merge_id).strip():
        raise ShoppingError("Mã gộp không hợp lệ")

    for line in guest_lines:
        _require_positive_int_quantity(line.quantity)

    payload_hash = _merge_payload_hash(guest_lines)

    async with transaction(db):
        cart_key = await repository.get_cart_key(db, account_key)
        if cart_key is None:
            raise CartNotFoundError()

        existing_hash = await repository.get_merge_payload_hash(
            db, account_key, merge_id
        )
        if existing_hash is not None:
            if existing_hash != payload_hash:
                raise MergeRequestConflictError()
            # Đã xử lý cùng payload → không cộng lại (AC-10, AC-11)
            items = await repository.list_cart_items(db, cart_key)
            return {variant_key: qty for _, variant_key, qty in items}

        inserted = await repository.insert_merge_request(
            db, account_key, merge_id, payload_hash
        )
        if not inserted:
            # Request đồng thời đã lưu mã — chỉ xác nhận, không cộng lại (AC-11)
            existing_hash = await repository.get_merge_payload_hash(
                db, account_key, merge_id
            )
            if existing_hash is None:
                raise ShoppingError("Không lưu được yêu cầu gộp giỏ")
            if existing_hash != payload_hash:
                raise MergeRequestConflictError()
            items = await repository.list_cart_items(db, cart_key)
            return {variant_key: qty for _, variant_key, qty in items}

        for line in guest_lines:
            stock = await availability.get_stock_quantity(line.variant_key)
            sellable = await availability.is_variant_sellable(line.variant_key)
            existing = await repository.get_cart_item_quantity(
                db, cart_key, line.variant_key
            )
            current_qty = existing[1] if existing else 0
            combined = current_qty + line.quantity

            if sellable and stock > 0:
                final_qty = min(combined, stock)
            else:
                # Hết hàng / ngừng bán: giữ số lượng đã chọn (cộng dồn), không về 0 [GD]/UC-18
                final_qty = combined

            if final_qty <= 0:
                continue

            if existing is None:
                await repository.insert_cart_item(
                    db, cart_key, line.variant_key, final_qty
                )
            else:
                await repository.update_cart_item_quantity(
                    db, existing[0], final_qty
                )

        items = await repository.list_cart_items(db, cart_key)
        return {variant_key: qty for _, variant_key, qty in items}


async def add_to_wishlist(
    db: AsyncSession,
    *,
    account_key: UUID,
    product_key: UUID,
    catalog: ProductCatalog,
) -> bool:
    """UC-38 AC-1 / AC-4: thả tim; trùng thì không tạo thêm. True nếu mới thêm."""
    if not await catalog.product_exists(product_key):
        raise ProductNotFoundError()

    async with transaction(db):
        wishlist_key = await repository.get_wishlist_key(db, account_key)
        if wishlist_key is None:
            raise WishlistNotFoundError()
        return await repository.insert_wishlist_item(db, wishlist_key, product_key)


async def remove_from_wishlist(
    db: AsyncSession, *, account_key: UUID, product_key: UUID
) -> None:
    """UC-38 AC-2: bỏ tim."""
    async with transaction(db):
        wishlist_key = await repository.get_wishlist_key(db, account_key)
        if wishlist_key is None:
            raise WishlistNotFoundError()
        deleted = await repository.delete_wishlist_item(
            db, wishlist_key, product_key
        )
        if not deleted:
            # Đã không còn trong list — idempotent nhẹ cho AC-2
            return


async def get_wishlist(
    db: AsyncSession,
    *,
    account_key: UUID,
    catalog: ProductCatalog,
    page: int = 1,
    page_size: int = _DEFAULT_WISHLIST_PAGE_SIZE,
) -> WishlistView:
    """UC-38 AC-3/6/7/8: danh sách mới thêm trước, có phân trang."""
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = _DEFAULT_WISHLIST_PAGE_SIZE

    wishlist_key = await repository.get_wishlist_key(db, account_key)
    if wishlist_key is None:
        raise WishlistNotFoundError()

    total = await repository.count_wishlist_items(db, wishlist_key)
    offset = (page - 1) * page_size
    product_keys = await repository.list_wishlist_product_keys(
        db, wishlist_key, limit=page_size, offset=offset
    )

    items: list[WishlistItemView] = []
    for product_key in product_keys:
        card = await catalog.get_product_card(product_key)
        items.append(
            WishlistItemView(
                product_key=card.product_key,
                product_id=card.product_id,
                name=card.name,
                image_url=card.image_url,
                min_price=to_vnd(card.min_price),
                is_active=card.is_active,
                can_open_detail=card.is_active,
            )
        )

    return WishlistView(
        account_key=account_key,
        items=tuple(items),
        page=page,
        page_size=page_size,
        total_items=total,
    )


async def is_product_in_wishlist(
    db: AsyncSession, *, account_key: UUID, product_key: UUID
) -> bool:
    wishlist_key = await repository.get_wishlist_key(db, account_key)
    if wishlist_key is None:
        raise WishlistNotFoundError()
    return await repository.wishlist_has_product(db, wishlist_key, product_key)
