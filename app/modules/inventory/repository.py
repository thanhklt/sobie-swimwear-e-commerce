"""Truy vấn bảng thuộc schema inventory."""

from sqlalchemy import text


async def restore_variant_stock(db, variant_key, quantity: int) -> None:
    result = await db.exec(text("""
        UPDATE inventory.stock SET stock_quantity = stock_quantity + :quantity
        WHERE stock_variant_key = :variant_key RETURNING stock_key
    """), params={"variant_key": variant_key, "quantity": quantity})
    if result.first() is None:
        raise ValueError("Không tìm thấy dòng tồn kho của biến thể cần hoàn.")
