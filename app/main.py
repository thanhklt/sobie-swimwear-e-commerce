"""Điểm khởi tạo ứng dụng và đăng ký router của 9 module; chưa triển khai.

Module: identity, catalog, shopping, ordering, payment, promotion, inventory, shipping, reporting.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.error.handlers import register_error_handlers
from app.modules.ordering.router import router as ordering_router
from app.modules.shopping.router import router as shopping_router
from app.shared.web.session import SessionMiddleware

version = "v1"


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Server is starting")
    yield
    print("Shutdown the server")


app = FastAPI(
    title="sobie-swimwear-e-commerce",
    description="Trang web thương mại điện tử bán đồ bơi của sobie",
    version=version,
    lifespan=life_span,
)
app.add_middleware(SessionMiddleware)
register_error_handlers(app)
app.include_router(shopping_router)
app.include_router(ordering_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to the Sobie Swimwear E-commerce API",
        "shopping_ui": "/dev/shopping",
        "ordering_ui": "/dev/ordering",
    }
