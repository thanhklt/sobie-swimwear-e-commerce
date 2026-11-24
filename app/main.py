"""Điểm khởi tạo ứng dụng và đăng ký router của 9 module.

Module: identity, catalog, shopping, ordering, payment, promotion, inventory, shipping, reporting.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.database.engine import session_factory
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.service import IdentityService
from app.error.handlers import register_error_handlers
from app.modules.identity.registration_challenges import close_challenge_store
from app.modules.identity.router import login_router, router as identity_router, storefront_identity_home
from app.security.session import SessionMiddleware

version = "v1"
API_PREFIX = f"/api/{version}"


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Server is starting")
    try:
        yield
    finally:
        await close_challenge_store()
        print("Shutdown the server")


app = FastAPI(
    title="sobie-swimwear-e-commerce",
    description="Trang web thương mại điện tử bán đồ bơi của sobie",
    version=version,
    lifespan=life_span,
)
app.state.identity_service = IdentityService(IdentityRepository(), session_factory)
app.add_middleware(SessionMiddleware, api_prefix=API_PREFIX)
app.mount("/static/css", StaticFiles(directory=Path(__file__).parent / "static" / "css"), name="static_css")
app.include_router(identity_router)
app.include_router(login_router, prefix=API_PREFIX)
register_error_handlers(app)


@app.get("/")
def root(request: Request):
    if "text/html" in request.headers.get("accept", ""):
        return storefront_identity_home(request)
    return JSONResponse({"message": "Welcome to the Sobie Swimwear E-commerce API"}, headers={"Vary": "Accept"})
