"""Standalone public shipping simulator entry point (default Docker port 8001)."""

from fastapi import FastAPI

from app.modules.shipping.public_router import router as public_shipping_router

app = FastAPI(
    title="Sobie Shipping Simulator",
    description="Trang giả lập cập nhật trạng thái vận chuyển, chỉ hiển thị mã đơn và trạng thái.",
    version="v1",
)
app.include_router(public_shipping_router)
