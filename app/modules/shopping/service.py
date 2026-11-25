"""Tầng Service của module shopping: nghiệp vụ và điều phối transaction.

Service công khai cho module khác:
- Khởi tạo giỏ hàng và danh sách yêu thích của tài khoản Khách hàng.
- Đọc các dòng giỏ của khách (cho ordering khi đặt hàng).
- Xóa các dòng đã đặt khỏi giỏ sau khi tạo đơn.

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""

import json
from hashlib import sha256
from typing import TYPE_CHECKING
from uuid import UUID

from app.database.transaction import transaction
from app.modules.catalog.service import get_cart_variants
from app.modules.inventory.service import get_stock_for_cart_merge
from app.modules.shopping import repository

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession


# UC-01 Đăng ký tài khoản — Main 7; 1b.4; E6 (specs/use-cases/identity/UC-01-register-account.md)
async def initialize_customer_shopping(db: "AsyncSession", *, account_key: UUID) -> None:
    await repository.insert_cart(db, account_key=account_key)
    await repository.insert_wishlist(db, account_key=account_key)


class CartMergeConflict(Exception):
    """A merge key was already used with a different cart."""


async def merge_guest_cart(session_factory, account_key, merge_key, quantities):
    normalized = sorted((str(key), quantity) for key, quantity in quantities.items())
    payload_hash = sha256(json.dumps(normalized).encode()).hexdigest()
    async with session_factory() as db, transaction(db):
        cart_key = await repository.lock_cart(db, account_key)
        previous = await repository.find_cart_merge(db, cart_key, merge_key)
        if previous is not None:
            if previous.payload_hash != payload_hash:
                raise CartMergeConflict
            return previous.result

        current = await repository.cart_quantities(db, account_key)
        variants = await get_cart_variants(db, quantities)
        stock = await get_stock_for_cart_merge(db, variants)
        result = []
        for variant_key, quantity in quantities.items():
            old = current.get(variant_key, 0)
            available = stock.get(variant_key, 0)
            variant = variants.get(variant_key)
            if not variant or not variant.sellable or not available:
                result.append({
                    "variant_key": str(variant_key), "sku": variant.variant_id if variant else None,
                    "quantity": old, "added": 0, "status": "unavailable",
                })
                continue
            total = min(old + quantity, available)
            await repository.set_cart_quantity(db, cart_key, variant_key, total)
            result.append({
                "variant_key": str(variant_key), "sku": variant.variant_id,
                "quantity": total, "added": max(0, total - old),
                "status": "limited" if total < old + quantity else "merged",
            })
        merged = {"items": result}
        await repository.record_cart_merge(db, cart_key, merge_key, payload_hash, merged)
        return merged


async def get_checkout_items(db, account_key):
    quantities = await repository.cart_quantities(db, account_key)
    variants = await get_cart_variants(db, quantities)
    return [
        {"name": variants[key].product_name, "sku": variants[key].variant_id, "quantity": quantity}
        for key, quantity in quantities.items() if key in variants
    ]
