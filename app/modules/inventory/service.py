"""Tầng Service của module inventory: nghiệp vụ và điều phối transaction.

Service công khai cho module khác:
- Đọc tồn kho theo biến thể (cho catalog, shopping, reporting).
- Trừ / cộng tồn trong transaction của bên gọi (cho ordering).
- Đọc giá vốn hiện tại (cho ordering, reporting).
- Tạo dòng tồn kho khi tạo biến thể (cho catalog).

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""

from contextlib import asynccontextmanager
from decimal import Decimal, ROUND_HALF_UP
import logging
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.modules.catalog import service as catalog
from app.modules.inventory import repository
from app.modules.inventory.schemas import ReceiptInput, ReceiptStatus, SupplierInput
from app.shared.database.transaction import transaction

logger = logging.getLogger(__name__)
PAGE_SIZE = 20
MAX_QUANTITY = 2_147_483_647


class InventoryError(Exception):
    def __init__(self, message: str, *, status_code: int = 400, field_errors: dict[str, str] | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.field_errors = field_errors or {}


@asynccontextmanager
async def _database():
    from app.shared.database.engine import session_factory

    try:
        async with session_factory() as db, transaction(db):
            yield db
    except IntegrityError as exc:
        if "supplier_name_normalized_uq" in str(exc.orig):
            raise InventoryError("Tên nhà cung cấp đã tồn tại", status_code=409,
                                 field_errors={"name": "Tên nhà cung cấp đã tồn tại"}) from exc
        logger.error("Inventory database integrity failure: %s", type(exc).__name__)
        raise InventoryError("Không thể lưu dữ liệu; vui lòng thử lại", status_code=503) from exc
    except (SQLAlchemyError, OSError) as exc:
        logger.error("Inventory database operation failed: %s", type(exc).__name__)
        raise InventoryError("Không thể xử lý dữ liệu; vui lòng thử lại", status_code=503) from exc
    except ValueError as exc:
        code = str(exc)
        if code == "duplicate_supplier_name":
            raise InventoryError("Tên nhà cung cấp đã tồn tại", status_code=409,
                                 field_errors={"name": "Tên nhà cung cấp đã tồn tại"}) from exc
        if code in {"supplier_code_exhausted", "receipt_code_exhausted"}:
            raise InventoryError("Đã hết dải mã tự nhiên được cấp", status_code=409) from exc
        if code == "supplier_not_found":
            raise InventoryError("Không tìm thấy nhà cung cấp", status_code=404) from exc
        raise


def _page(page: int) -> int:
    if type(page) is not int or page < 1:
        raise InventoryError("Trang không hợp lệ")
    return (page - 1) * PAGE_SIZE


async def _supplier(db, supplier_key: UUID, *, lock: bool = False) -> dict:
    row = await repository.get_supplier(db, supplier_key, lock=lock)
    if row is None:
        raise InventoryError("Không tìm thấy nhà cung cấp", status_code=404)
    return row


async def _receipt(db, receipt_key: UUID, *, lock: bool = False) -> dict:
    row = await repository.get_receipt(db, receipt_key, lock=lock)
    if row is None:
        raise InventoryError("Không tìm thấy phiếu nhập", status_code=404)
    return row


def _draft(receipt: dict) -> None:
    if receipt["goods_receipt_status"] != "DRAFT":
        raise InventoryError("Phiếu không còn ở trạng thái Nháp", status_code=409)


async def list_suppliers(*, q: str = "", page: int = 1) -> dict:
    offset = _page(page)
    async with _database() as db:
        suppliers, total = await repository.list_suppliers(db, q=q, offset=offset, limit=PAGE_SIZE)
        return dict(suppliers=suppliers, total=total, page=page, page_size=PAGE_SIZE, q=q.strip())


async def get_supplier(supplier_key: UUID) -> dict:
    async with _database() as db:
        return await _supplier(db, supplier_key)


async def save_supplier(data: SupplierInput, *, supplier_key: UUID | None = None) -> dict:
    async with _database() as db:
        if supplier_key is None:
            return await repository.create_supplier(db, **data.model_dump())
        await _supplier(db, supplier_key, lock=True)
        return await repository.update_supplier(db, supplier_key, **data.model_dump())


async def deactivate_supplier(supplier_key: UUID) -> None:
    async with _database() as db:
        supplier = await _supplier(db, supplier_key, lock=True)
        if supplier["supplier_status"] != "ACTIVE":
            raise InventoryError("Nhà cung cấp đã ngừng hợp tác", status_code=409)
        await repository.deactivate_supplier(db, supplier_key)


async def delete_supplier(supplier_key: UUID) -> None:
    async with _database() as db:
        await _supplier(db, supplier_key, lock=True)
        if await repository.supplier_has_receipts(db, supplier_key):
            raise InventoryError("Nhà cung cấp đã có phiếu nhập; hãy chọn Ngừng hợp tác", status_code=409)
        await repository.delete_supplier(db, supplier_key)


async def list_receipts(*, status: str | None = None, supplier_key: UUID | None = None, page: int = 1) -> dict:
    offset = _page(page)
    if status is not None and status not in {item.value for item in ReceiptStatus}:
        raise InventoryError("Trạng thái phiếu nhập không hợp lệ")
    async with _database() as db:
        if supplier_key is not None:
            await _supplier(db, supplier_key)
        rows, total = await repository.list_receipts(db, status=status, supplier_key=supplier_key,
                                                    offset=offset, limit=PAGE_SIZE)
        suppliers, _ = await repository.list_suppliers(db, limit=None)
        return dict(receipts=rows, total=total, page=page, page_size=PAGE_SIZE, status=status,
                    supplier_key=supplier_key, suppliers=suppliers)


async def _form_data(db) -> dict:
    variants, _ = await catalog.list_inventory_variants(db, limit=None)
    return dict(suppliers=await repository.active_suppliers(db), variants=variants)


async def receipt_form_data() -> dict:
    async with _database() as db:
        return await _form_data(db)


async def get_receipt(receipt_key: UUID) -> dict:
    async with _database() as db:
        receipt = await _receipt(db, receipt_key)
        supplier = await _supplier(db, receipt["goods_receipt_supplier_key"])
        receipt["supplier_name"] = supplier["supplier_name"]
        lines = await repository.receipt_lines(db, receipt_key)
        metadata = {row["variant_key"]: row for row in await catalog.get_inventory_variants(
            db, [line["goods_receipt_detail_variant_key"] for line in lines])}
        lines = [line | metadata.get(line["goods_receipt_detail_variant_key"], {}) for line in lines]
        return dict(receipt=receipt, lines=lines, **(await _form_data(db)))


async def save_receipt(data: ReceiptInput, account_key: UUID, *, receipt_key: UUID | None = None) -> dict:
    async with _database() as db:
        if receipt_key is not None:
            _draft(await _receipt(db, receipt_key, lock=True))
        supplier = await _supplier(db, data.supplier_key, lock=True)
        if supplier["supplier_status"] != "ACTIVE":
            raise InventoryError("Nhà cung cấp đã ngừng hợp tác", status_code=409,
                                 field_errors={"supplier_key": "Chọn nhà cung cấp đang hợp tác"})
        keys = [line.variant_key for line in data.lines]
        variants = await catalog.get_inventory_variants(db, keys, lock=True)
        if {row["variant_key"] for row in variants} != set(keys):
            raise InventoryError("Không tìm thấy biến thể", status_code=404,
                                 field_errors={"lines": "Một hoặc nhiều biến thể không tồn tại"})
        if receipt_key is None:
            receipt = await repository.create_receipt(db, supplier_key=data.supplier_key,
                                                       account_key=account_key, total=data.total_price)
            receipt_key = receipt["goods_receipt_key"]
        else:
            await repository.update_receipt(db, receipt_key, supplier_key=data.supplier_key, total=data.total_price)
        await repository.replace_receipt_lines(db, receipt_key, [line.model_dump() | {"total_price": line.total_price}
                                                                 for line in data.lines])
        return await _receipt(db, receipt_key)


async def cancel_receipt(receipt_key: UUID) -> None:
    async with _database() as db:
        _draft(await _receipt(db, receipt_key, lock=True))
        await repository.set_receipt_status(db, receipt_key, "CANCELLED")


async def _locked_stocks(db, keys: list[UUID]) -> dict[UUID, dict]:
    stocks = {row["stock_variant_key"]: row for row in await repository.get_stocks(db, keys, lock=True)}
    if set(stocks) != set(keys):
        raise InventoryError("Thiếu dòng tồn kho; thao tác chưa được lưu", status_code=503)
    return stocks


async def confirm_receipt(receipt_key: UUID) -> None:
    async with _database() as db:
        receipt = await _receipt(db, receipt_key, lock=True)
        _draft(receipt)
        stored = await repository.receipt_lines(db, receipt_key)
        try:
            data = ReceiptInput(supplier_key=receipt["goods_receipt_supplier_key"], lines=[
                dict(variant_key=line["goods_receipt_detail_variant_key"],
                     quantity=line["goods_receipt_detail_quantity"], unit_price=int(line["goods_receipt_detail_unit_price"]))
                for line in stored])
        except ValidationError as exc:
            raise InventoryError("Chi tiết phiếu nhập không hợp lệ", status_code=503) from exc
        if data.total_price != receipt["goods_receipt_final_price"]:
            raise InventoryError("Tổng tiền phiếu không khớp chi tiết", status_code=503)
        keys = [line.variant_key for line in data.lines]
        metadata = await catalog.get_inventory_variants(db, keys, lock=True)
        if {row["variant_key"] for row in metadata} != set(keys):
            raise InventoryError("Không tìm thấy biến thể", status_code=404)
        stocks = await _locked_stocks(db, keys)
        for line in sorted(data.lines, key=lambda item: item.variant_key):
            stock = stocks[line.variant_key]
            quantity = stock["stock_quantity"] + line.quantity
            if quantity > MAX_QUANTITY:
                raise InventoryError("Số lượng tồn vượt giới hạn lưu trữ", status_code=409)
            value = Decimal(stock["stock_quantity"]) * stock["stock_cost_price"] + Decimal(line.total_price)
            cost = int((value / Decimal(quantity)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
            await repository.update_stock(db, line.variant_key, quantity=quantity, cost_price=cost)
        await repository.set_receipt_status(db, receipt_key, "CONFIRMED")
    # Cache failure cannot undo a committed receipt or ask staff to confirm it again.
    try:
        await catalog.bump_catalog_version()
    except Exception:
        logger.warning("Catalog cache invalidation failed after confirming receipt %s", receipt["goods_receipt_id"])


async def list_stock(*, q: str = "", category_key: UUID | None = None, page: int = 1) -> dict:
    offset = _page(page)
    async with _database() as db:
        categories = await catalog.inventory_categories(db)
        if category_key is not None and category_key not in {row["category_key"] for row in categories}:
            raise InventoryError("Danh mục không hợp lệ")
        variants, total = await catalog.list_inventory_variants(db, q=q, category_key=category_key,
                                                               offset=offset, limit=PAGE_SIZE)
        stocks = await get_stock(db, [row["variant_key"] for row in variants])
        if len(stocks) != len(variants):
            raise InventoryError("Thiếu dòng tồn kho", status_code=503)
        rows = [variant | {"stock_quantity": stocks[variant["variant_key"]]["stock_quantity"],
                           "is_low_stock": stocks[variant["variant_key"]]["stock_quantity"] <= 5}
                for variant in variants]
        return dict(stocks=rows, total=total, page=page, page_size=PAGE_SIZE, q=q.strip(),
                    category_key=category_key, categories=categories)


async def get_stock(db, variant_keys: list[UUID]) -> dict[UUID, dict]:
    return {row["stock_variant_key"]: row for row in await repository.get_stocks(db, variant_keys)}


async def create_stock(db, variant_key: UUID) -> dict:
    return await repository.create_stock(db, variant_key)


def _quantities(quantities: dict[UUID, int]) -> None:
    if any(not isinstance(key, UUID) or type(value) is not int or not 1 <= value <= MAX_QUANTITY
           for key, value in quantities.items()):
        raise InventoryError("Số lượng phải là số nguyên dương trong giới hạn lưu trữ")


async def deduct_stock(db, quantities: dict[UUID, int]) -> dict[UUID, dict]:
    """Caller owns transaction and order idempotency; never commits independently."""
    _quantities(quantities)
    stocks = await _locked_stocks(db, list(quantities))
    if any(stocks[key]["stock_quantity"] < value for key, value in quantities.items()):
        raise InventoryError("Không đủ tồn kho", status_code=409)
    result = {}
    for key in sorted(quantities):
        row = await repository.adjust_stock(db, key, -quantities[key])
        if row is None:
            raise InventoryError("Không đủ tồn kho", status_code=409)
        result[key] = row
    return result


async def restore_stock(db, quantities: dict[UUID, int]) -> None:
    """UC-35: restore existing rows without changing cost or catalog sale status."""
    _quantities(quantities)
    stocks = await _locked_stocks(db, list(quantities))
    if any(stocks[key]["stock_quantity"] + value > MAX_QUANTITY for key, value in quantities.items()):
        raise InventoryError("Số lượng tồn vượt giới hạn lưu trữ", status_code=409)
    for key in sorted(quantities):
        if await repository.adjust_stock(db, key, quantities[key]) is None:
            raise InventoryError("Không thể cộng lại tồn kho", status_code=503)


async def has_receipt_references(db, variant_keys: list[UUID], *, confirmed_only: bool = False) -> bool:
    """Catalog holds product locks; plain read avoids receipt/product lock inversion."""
    return await repository.has_receipt_references(db, variant_keys, confirmed_only=confirmed_only)
