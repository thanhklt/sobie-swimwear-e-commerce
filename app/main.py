"""Điểm khởi tạo ứng dụng và đăng ký router của 9 module; chưa triển khai.

Module: identity, catalog, shopping, ordering, payment, promotion, inventory, shipping, reporting.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.modules.catalog.router import router as catalog_router

from app.error.handlers import register_error_handlers
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
app.include_router(catalog_router)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/")
def root():
    return {"message": "Welcome to the Sobie Swimwear E-commerce API"}
