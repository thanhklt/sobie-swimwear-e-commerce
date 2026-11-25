"""Tầng Repository của module inventory: truy vấn các bảng do module sở hữu:
- inventory.supplier
- inventory.goods_receipt
- inventory.goods_receipt_detail
- inventory.stock

Không truy vấn bảng của module khác và không tự mở/commit/rollback transaction.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import TextClause, bindparam, text
from sqlalchemy.exc import DBAPIError

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession

_SUPPLIER_COLUMNS = (
    "supplier_key, supplier_id, supplier_name, supplier_phone_number, "
    "supplier_email, supplier_address, supplier_status"
)
_RECEIPT_COLUMNS = (
    "goods_receipt_key, goods_receipt_id, goods_receipt_final_price, "
    "goods_receipt_status, goods_receipt_created_date, "
    "goods_receipt_supplier_key, goods_receipt_account_key"
)
_RECEIPT_LIST_COLUMNS = (
    "r.goods_receipt_key, r.goods_receipt_id, r.goods_receipt_final_price, "
    "r.goods_receipt_status, r.goods_receipt_created_date, "
    "r.goods_receipt_supplier_key, r.goods_receipt_account_key, s.supplier_name"
)
_RECEIPT_DETAIL_COLUMNS = (
    "goods_receipt_detail_key, goods_receipt_detail_goods_receipt_key, "
    "goods_receipt_detail_variant_key, goods_receipt_detail_quantity, "
    "goods_receipt_detail_unit_price, goods_receipt_detail_total_price"
)
_STOCK_COLUMNS = "stock_key, stock_variant_key, stock_quantity, stock_cost_price"

_SUPPLIER_WRITE_LOCK = text("SELECT pg_advisory_xact_lock(21034, 1)")

_SEQUENCE_CONFIG: dict[str, tuple[str, str, TextClause, TextClause]] = {
    "supplier": (
        "NCC",
        "supplier_code_exhausted",
        text(
            """
            SELECT last_value
            FROM pg_sequences
            WHERE schemaname = 'inventory'
              AND sequencename = 'supplier_number_seq'
            """
        ),
        text("SELECT nextval('inventory.supplier_number_seq')"),
    ),
    "receipt": (
        "PN",
        "receipt_code_exhausted",
        text(
            """
            SELECT last_value
            FROM pg_sequences
            WHERE schemaname = 'inventory'
              AND sequencename = 'goods_receipt_number_seq'
            """
        ),
        text("SELECT nextval('inventory.goods_receipt_number_seq')"),
    ),
}

_COUNT_SUPPLIERS_ALL = text("SELECT count(*) FROM inventory.supplier")
_COUNT_SUPPLIERS_FILTERED = text(
    """
    SELECT count(*)
    FROM inventory.supplier
    WHERE lower(btrim(supplier_name)) LIKE lower(:pattern) ESCAPE '\\'
    """
)
_LIST_SUPPLIERS_ALL = text(
    f"""
    SELECT {_SUPPLIER_COLUMNS}
    FROM inventory.supplier
    ORDER BY supplier_name ASC, supplier_id ASC
    LIMIT :limit OFFSET :offset
    """
)
_LIST_SUPPLIERS_FILTERED = text(
    f"""
    SELECT {_SUPPLIER_COLUMNS}
    FROM inventory.supplier
    WHERE lower(btrim(supplier_name)) LIKE lower(:pattern) ESCAPE '\\'
    ORDER BY supplier_name ASC, supplier_id ASC
    LIMIT :limit OFFSET :offset
    """
)

_GET_SUPPLIER = text(
    f"SELECT {_SUPPLIER_COLUMNS} FROM inventory.supplier WHERE supplier_key = :supplier_key"
)
_GET_SUPPLIER_FOR_UPDATE = text(
    f"SELECT {_SUPPLIER_COLUMNS} FROM inventory.supplier WHERE supplier_key = :supplier_key FOR UPDATE"
)
_ACTIVE_SUPPLIERS = text(
    f"""
    SELECT {_SUPPLIER_COLUMNS}
    FROM inventory.supplier
    WHERE supplier_status = 'ACTIVE'
    ORDER BY supplier_name ASC, supplier_id ASC
    """
)

_SUPPLIER_NAME_EXISTS = text(
    """
    SELECT EXISTS (
        SELECT 1
        FROM inventory.supplier
        WHERE lower(btrim(supplier_name)) = lower(:name)
    )
    """
)
_SUPPLIER_NAME_EXISTS_EXCLUDING = text(
    """
    SELECT EXISTS (
        SELECT 1
        FROM inventory.supplier
        WHERE lower(btrim(supplier_name)) = lower(:name)
          AND supplier_key <> :exclude_key
    )
    """
)

_INSERT_SUPPLIER = text(
    f"""
    INSERT INTO inventory.supplier (
        supplier_id,
        supplier_name,
        supplier_phone_number,
        supplier_email,
        supplier_address,
        supplier_status
    )
    VALUES (
        :supplier_id,
        :supplier_name,
        :supplier_phone_number,
        :supplier_email,
        :supplier_address,
        'ACTIVE'
    )
    RETURNING {_SUPPLIER_COLUMNS}
    """
)
_UPDATE_SUPPLIER = text(
    f"""
    UPDATE inventory.supplier
    SET supplier_name = :supplier_name,
        supplier_phone_number = :supplier_phone_number,
        supplier_email = :supplier_email,
        supplier_address = :supplier_address
    WHERE supplier_key = :supplier_key
    RETURNING {_SUPPLIER_COLUMNS}
    """
)
_DEACTIVATE_SUPPLIER = text(
    """
    UPDATE inventory.supplier
    SET supplier_status = 'INACTIVE'
    WHERE supplier_key = :supplier_key
    """
)
_SUPPLIER_HAS_RECEIPTS = text(
    """
    SELECT EXISTS (
        SELECT 1
        FROM inventory.goods_receipt
        WHERE goods_receipt_supplier_key = :supplier_key
    )
    """
)
_DELETE_SUPPLIER = text(
    "DELETE FROM inventory.supplier WHERE supplier_key = :supplier_key"
)

_GET_RECEIPT = text(
    f"SELECT {_RECEIPT_COLUMNS} FROM inventory.goods_receipt WHERE goods_receipt_key = :receipt_key"
)
_GET_RECEIPT_FOR_UPDATE = text(
    f"SELECT {_RECEIPT_COLUMNS} FROM inventory.goods_receipt WHERE goods_receipt_key = :receipt_key FOR UPDATE"
)
_RECEIPT_LINES = text(
    f"""
    SELECT {_RECEIPT_DETAIL_COLUMNS}
    FROM inventory.goods_receipt_detail
    WHERE goods_receipt_detail_goods_receipt_key = :receipt_key
    ORDER BY goods_receipt_detail_variant_key ASC
    """
)
_INSERT_RECEIPT = text(
    f"""
    INSERT INTO inventory.goods_receipt (
        goods_receipt_id,
        goods_receipt_final_price,
        goods_receipt_status,
        goods_receipt_created_date,
        goods_receipt_supplier_key,
        goods_receipt_account_key
    )
    VALUES (
        :goods_receipt_id,
        :total,
        'DRAFT',
        now(),
        :supplier_key,
        :account_key
    )
    RETURNING {_RECEIPT_COLUMNS}
    """
)
_DELETE_RECEIPT_LINES = text(
    """
    DELETE FROM inventory.goods_receipt_detail
    WHERE goods_receipt_detail_goods_receipt_key = :receipt_key
    """
)
_INSERT_RECEIPT_LINE = text(
    """
    INSERT INTO inventory.goods_receipt_detail (
        goods_receipt_detail_goods_receipt_key,
        goods_receipt_detail_variant_key,
        goods_receipt_detail_quantity,
        goods_receipt_detail_unit_price,
        goods_receipt_detail_total_price
    )
    VALUES (
        :receipt_key,
        :variant_key,
        :quantity,
        :unit_price,
        :total_price
    )
    """
)
_UPDATE_RECEIPT = text(
    """
    UPDATE inventory.goods_receipt
    SET goods_receipt_supplier_key = :supplier_key,
        goods_receipt_final_price = :total
    WHERE goods_receipt_key = :receipt_key
    """
)
_SET_RECEIPT_STATUS = text(
    """
    UPDATE inventory.goods_receipt
    SET goods_receipt_status = :status
    WHERE goods_receipt_key = :receipt_key
    """
)

_GET_STOCKS = text(
    f"""
    SELECT {_STOCK_COLUMNS}
    FROM inventory.stock
    WHERE stock_variant_key IN :variant_keys
    ORDER BY stock_variant_key ASC
    """
).bindparams(bindparam("variant_keys", expanding=True))
_GET_STOCKS_FOR_UPDATE = text(
    f"""
    SELECT {_STOCK_COLUMNS}
    FROM inventory.stock
    WHERE stock_variant_key IN :variant_keys
    ORDER BY stock_variant_key ASC
    FOR UPDATE
    """
).bindparams(bindparam("variant_keys", expanding=True))
_INSERT_STOCK = text(
    f"""
    INSERT INTO inventory.stock (stock_variant_key, stock_quantity, stock_cost_price)
    VALUES (:variant_key, 0, 0)
    RETURNING {_STOCK_COLUMNS}
    """
)
_UPDATE_STOCK = text(
    """
    UPDATE inventory.stock
    SET stock_quantity = :quantity,
        stock_cost_price = :cost_price
    WHERE stock_variant_key = :variant_key
    """
)
_ADJUST_STOCK = text(
    f"""
    UPDATE inventory.stock
    SET stock_quantity = stock_quantity + :quantity_delta
    WHERE stock_variant_key = :variant_key
      AND stock_quantity + :quantity_delta >= 0
    RETURNING {_STOCK_COLUMNS}
    """
)

_HAS_ANY_RECEIPT_REFERENCES = text(
    """
    SELECT EXISTS (
        SELECT 1
        FROM inventory.goods_receipt_detail
        WHERE goods_receipt_detail_variant_key IN :variant_keys
    )
    """
).bindparams(bindparam("variant_keys", expanding=True))
_HAS_CONFIRMED_RECEIPT_REFERENCES = text(
    """
    SELECT EXISTS (
        SELECT 1
        FROM inventory.goods_receipt_detail AS d
        JOIN inventory.goods_receipt AS r
          ON r.goods_receipt_key = d.goods_receipt_detail_goods_receipt_key
        WHERE d.goods_receipt_detail_variant_key IN :variant_keys
          AND r.goods_receipt_status = 'CONFIRMED'
    )
    """
).bindparams(bindparam("variant_keys", expanding=True))


def _row_dict(row: Mapping[str, Any]) -> dict[str, Any]:
    return dict(row)


def _escape_like(value: str) -> str:
    """Escape ký tự đại diện LIKE để tìm chuỗi con theo nghĩa đen."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _normalize_supplier_fields(
    *,
    name: str,
    phone_number: str,
    email: str,
    address: str,
) -> dict[str, str | None]:
    return {
        "supplier_name": name.strip(),
        "supplier_phone_number": phone_number.strip(),
        "supplier_email": (email or "").strip() or None,
        "supplier_address": (address or "").strip() or None,
    }


async def _allocate_code(db: AsyncSession, kind: str) -> str:
    """Cấp phát mã tự nhiên đơn điệu qua sequence trong DB, chặn vượt 9999."""
    prefix, exhausted_error, check_stmt, nextval_stmt = _SEQUENCE_CONFIG[kind]
    # Kiểm tra trước watermark để báo lỗi nghiệp vụ mà không làm hỏng transaction hiện tại.
    last_value = (await db.exec(check_stmt)).scalar_one_or_none()
    if last_value is not None and int(last_value) >= 9999:
        raise ValueError(exhausted_error)

    try:
        seq_value = int((await db.exec(nextval_stmt)).scalar_one())
    except DBAPIError as exc:
        if getattr(exc.orig, "sqlstate", None) == "2200H":
            raise ValueError(exhausted_error) from exc
        raise

    if seq_value < 1 or seq_value > 9999:
        raise ValueError(exhausted_error)
    return f"{prefix}-{seq_value:04d}"


async def list_suppliers(
    db: AsyncSession,
    *,
    q: str = "",
    offset: int = 0,
    limit: int | None = 20,
) -> tuple[list[dict[str, Any]], int]:
    """Liệt kê nhà cung cấp phân trang và tìm chuỗi con phân biệt dấu, không phân biệt hoa/thường."""
    term = q.strip()
    if term:
        pattern = f"%{_escape_like(term)}%"
        total = int(
            (await db.exec(_COUNT_SUPPLIERS_FILTERED, params={"pattern": pattern})).scalar_one()
        )
        rows = (
            await db.exec(
                _LIST_SUPPLIERS_FILTERED,
                params={"pattern": pattern, "limit": limit, "offset": offset},
            )
        ).mappings().all()
    else:
        total = int((await db.exec(_COUNT_SUPPLIERS_ALL)).scalar_one())
        rows = (
            await db.exec(
                _LIST_SUPPLIERS_ALL,
                params={"limit": limit, "offset": offset},
            )
        ).mappings().all()
    return [_row_dict(row) for row in rows], total


async def get_supplier(
    db: AsyncSession,
    supplier_key: UUID,
    *,
    lock: bool = False,
) -> dict[str, Any] | None:
    """Đọc một nhà cung cấp theo khóa chính, tùy chọn khóa dòng FOR UPDATE."""
    stmt = _GET_SUPPLIER_FOR_UPDATE if lock else _GET_SUPPLIER
    row = (await db.exec(stmt, params={"supplier_key": supplier_key})).mappings().one_or_none()
    return _row_dict(row) if row is not None else None


async def active_suppliers(db: AsyncSession) -> list[dict[str, Any]]:
    """Lấy toàn bộ nhà cung cấp đang hợp tác theo thứ tự tên và mã."""
    rows = (await db.exec(_ACTIVE_SUPPLIERS)).mappings().all()
    return [_row_dict(row) for row in rows]


async def supplier_name_exists(
    db: AsyncSession,
    name: str,
    *,
    exclude_key: UUID | None = None,
) -> bool:
    """Kiểm tra trùng tên nhà cung cấp (trim, không phân biệt hoa/thường, phân biệt dấu)."""
    clean_name = name.strip()
    if exclude_key is None:
        result = await db.exec(_SUPPLIER_NAME_EXISTS, params={"name": clean_name})
    else:
        result = await db.exec(
            _SUPPLIER_NAME_EXISTS_EXCLUDING,
            params={"name": clean_name, "exclude_key": exclude_key},
        )
    return bool(result.scalar_one())


async def create_supplier(
    db: AsyncSession,
    *,
    name: str,
    phone_number: str,
    email: str,
    address: str,
) -> dict[str, Any]:
    """Tạo nhà cung cấp mới với khóa tuần tự ghi và cấp mã NCC-xxxx đơn điệu."""
    fields = _normalize_supplier_fields(
        name=name,
        phone_number=phone_number,
        email=email,
        address=address,
    )
    await db.exec(_SUPPLIER_WRITE_LOCK)
    if await supplier_name_exists(db, str(fields["supplier_name"])):
        raise ValueError("duplicate_supplier_name")

    supplier_id = await _allocate_code(db, "supplier")
    row = (
        await db.exec(
            _INSERT_SUPPLIER,
            params={"supplier_id": supplier_id, **fields},
        )
    ).mappings().one()
    return _row_dict(row)


async def update_supplier(
    db: AsyncSession,
    supplier_key: UUID,
    *,
    name: str,
    phone_number: str,
    email: str,
    address: str,
) -> dict[str, Any]:
    """Cập nhật nhà cung cấp, tuần tự hóa kiểm tra trùng tên loại trừ chính bản ghi này."""
    fields = _normalize_supplier_fields(
        name=name,
        phone_number=phone_number,
        email=email,
        address=address,
    )
    await db.exec(_SUPPLIER_WRITE_LOCK)
    if await supplier_name_exists(db, str(fields["supplier_name"]), exclude_key=supplier_key):
        raise ValueError("duplicate_supplier_name")

    row = (
        await db.exec(
            _UPDATE_SUPPLIER,
            params={"supplier_key": supplier_key, **fields},
        )
    ).mappings().one_or_none()
    if row is None:
        raise ValueError("supplier_not_found")
    return _row_dict(row)


async def deactivate_supplier(db: AsyncSession, supplier_key: UUID) -> None:
    """Chuyển trạng thái nhà cung cấp sang INACTIVE (service giữ khóa dòng)."""
    await db.exec(_DEACTIVATE_SUPPLIER, params={"supplier_key": supplier_key})


async def supplier_has_receipts(db: AsyncSession, supplier_key: UUID) -> bool:
    """Kiểm tra nhà cung cấp có phiếu nhập tham chiếu ở bất kỳ trạng thái nào hay không."""
    result = await db.exec(_SUPPLIER_HAS_RECEIPTS, params={"supplier_key": supplier_key})
    return bool(result.scalar_one())


async def delete_supplier(db: AsyncSession, supplier_key: UUID) -> None:
    """Xóa hẳn nhà cung cấp chưa có phiếu nhập (service giữ khóa dòng)."""
    await db.exec(_DELETE_SUPPLIER, params={"supplier_key": supplier_key})


async def list_receipts(
    db: AsyncSession,
    *,
    status: str | None = None,
    supplier_key: UUID | None = None,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    """Liệt kê phiếu nhập kèm tên nhà cung cấp, lọc trạng thái và nhà cung cấp."""
    conditions: list[str] = []
    filter_params: dict[str, Any] = {}
    if status is not None:
        conditions.append("r.goods_receipt_status = :status")
        filter_params["status"] = status
    if supplier_key is not None:
        conditions.append("r.goods_receipt_supplier_key = :supplier_key")
        filter_params["supplier_key"] = supplier_key

    where_sql = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    count_stmt = text(f"SELECT count(*) FROM inventory.goods_receipt AS r {where_sql}")
    list_stmt = text(
        f"""
        SELECT {_RECEIPT_LIST_COLUMNS}
        FROM inventory.goods_receipt AS r
        JOIN inventory.supplier AS s
          ON s.supplier_key = r.goods_receipt_supplier_key
        {where_sql}
        ORDER BY r.goods_receipt_created_date DESC, r.goods_receipt_id DESC
        LIMIT :limit OFFSET :offset
        """
    )

    total = int((await db.exec(count_stmt, params=filter_params)).scalar_one())
    rows = (
        await db.exec(
            list_stmt,
            params={**filter_params, "limit": limit, "offset": offset},
        )
    ).mappings().all()
    return [_row_dict(row) for row in rows], total


async def get_receipt(
    db: AsyncSession,
    receipt_key: UUID,
    *,
    lock: bool = False,
) -> dict[str, Any] | None:
    """Đọc các trường của phiếu nhập, tùy chọn khóa dòng FOR UPDATE."""
    stmt = _GET_RECEIPT_FOR_UPDATE if lock else _GET_RECEIPT
    row = (await db.exec(stmt, params={"receipt_key": receipt_key})).mappings().one_or_none()
    return _row_dict(row) if row is not None else None


async def receipt_lines(db: AsyncSession, receipt_key: UUID) -> list[dict[str, Any]]:
    """Đọc các dòng chi tiết của phiếu nhập theo thứ tự variant_key tăng dần."""
    rows = (await db.exec(_RECEIPT_LINES, params={"receipt_key": receipt_key})).mappings().all()
    return [_row_dict(row) for row in rows]


async def create_receipt(
    db: AsyncSession,
    *,
    supplier_key: UUID,
    account_key: UUID,
    total: int,
) -> dict[str, Any]:
    """Tạo phiếu nhập DRAFT mới với mã PN-xxxx đơn điệu và thời gian UTC từ DB."""
    receipt_id = await _allocate_code(db, "receipt")
    row = (
        await db.exec(
            _INSERT_RECEIPT,
            params={
                "goods_receipt_id": receipt_id,
                "total": total,
                "supplier_key": supplier_key,
                "account_key": account_key,
            },
        )
    ).mappings().one()
    return _row_dict(row)


async def replace_receipt_lines(
    db: AsyncSession,
    receipt_key: UUID,
    lines: list[dict[str, Any]],
) -> None:
    """Thay thế toàn bộ dòng chi tiết của phiếu nhập (service giữ khóa phiếu)."""
    await db.exec(_DELETE_RECEIPT_LINES, params={"receipt_key": receipt_key})
    if not lines:
        return
    await db.exec(
        _INSERT_RECEIPT_LINE,
        params=[
            {
                "receipt_key": receipt_key,
                "variant_key": line["variant_key"],
                "quantity": line["quantity"],
                "unit_price": line["unit_price"],
                "total_price": line["total_price"],
            }
            for line in lines
        ],
    )


async def update_receipt(
    db: AsyncSession,
    receipt_key: UUID,
    *,
    supplier_key: UUID,
    total: int,
) -> None:
    """Cập nhật nhà cung cấp và tổng tiền của phiếu nhập."""
    await db.exec(
        _UPDATE_RECEIPT,
        params={
            "receipt_key": receipt_key,
            "supplier_key": supplier_key,
            "total": total,
        },
    )


async def set_receipt_status(db: AsyncSession, receipt_key: UUID, status: str) -> None:
    """Cập nhật trạng thái phiếu nhập."""
    await db.exec(
        _SET_RECEIPT_STATUS,
        params={"receipt_key": receipt_key, "status": status},
    )


async def get_stocks(
    db: AsyncSession,
    variant_keys: list[UUID],
    *,
    lock: bool = False,
) -> list[dict[str, Any]]:
    """Đọc các dòng tồn kho theo thứ tự stock_variant_key ASC, tùy chọn khóa FOR UPDATE."""
    if not variant_keys:
        return []
    unique_keys = tuple(dict.fromkeys(variant_keys))
    stmt = _GET_STOCKS_FOR_UPDATE if lock else _GET_STOCKS
    rows = (await db.exec(stmt, params={"variant_keys": unique_keys})).mappings().all()
    return [_row_dict(row) for row in rows]


async def create_stock(db: AsyncSession, variant_key: UUID) -> dict[str, Any]:
    """Tạo dòng tồn kho ban đầu với số lượng 0 và giá vốn 0."""
    row = (await db.exec(_INSERT_STOCK, params={"variant_key": variant_key})).mappings().one()
    return _row_dict(row)


async def update_stock(
    db: AsyncSession,
    variant_key: UUID,
    *,
    quantity: int,
    cost_price: int,
) -> None:
    """Cập nhật tồn kho và giá vốn sau khi service đã khóa dòng tồn kho."""
    await db.exec(
        _UPDATE_STOCK,
        params={
            "variant_key": variant_key,
            "quantity": quantity,
            "cost_price": cost_price,
        },
    )


async def adjust_stock(
    db: AsyncSession,
    variant_key: UUID,
    quantity_delta: int,
) -> dict[str, Any] | None:
    """Điều chỉnh nguyên tử số lượng tồn kho, bảo đảm không âm và giữ nguyên giá vốn."""
    row = (
        await db.exec(
            _ADJUST_STOCK,
            params={"variant_key": variant_key, "quantity_delta": quantity_delta},
        )
    ).mappings().one_or_none()
    return _row_dict(row) if row is not None else None


async def has_receipt_references(
    db: AsyncSession,
    variant_keys: list[UUID],
    *,
    confirmed_only: bool = False,
) -> bool:
    """Kiểm tra biến thể có được tham chiếu bởi phiếu nhập nào hay không (không khóa phiếu)."""
    if not variant_keys:
        return False
    unique_keys = tuple(dict.fromkeys(variant_keys))
    stmt = _HAS_CONFIRMED_RECEIPT_REFERENCES if confirmed_only else _HAS_ANY_RECEIPT_REFERENCES
    result = await db.exec(stmt, params={"variant_keys": unique_keys})
    return bool(result.scalar_one())
