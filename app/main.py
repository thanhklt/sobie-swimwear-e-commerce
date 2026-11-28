"""Điểm khởi tạo ứng dụng gồm 10 module và đăng ký các router.

Module: identity, catalog, shopping, ordering, payment, promotion, inventory, shipping, reporting, notification.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.database.engine import session_factory
from app.modules.catalog.router import storefront_home
from app.redis.engine import close_redis, get_redis
from app.modules.identity.service import build_identity_services
from app.error.handlers import register_error_handlers
from app.modules.identity.router import router as identity_router
from app.modules.notification import facade as notification_facade
from app.modules.ordering.router import router as ordering_router
from app.modules.shopping.router import router as shopping_router
from app.security.session import SessionMiddleware
from app.shared.web.rendering import register_templates

version = "v1"
API_PREFIX = f"/api/{version}"


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Server is starting")
    try:
        yield
    finally:
        await close_redis()
        print("Shutdown the server")


app = FastAPI(
    title="sobie-swimwear-e-commerce",
    description="Trang web thương mại điện tử bán đồ bơi của sobie",
    version=version,
    lifespan=life_span,
)
app.state.identity = build_identity_services(
    session_factory, redis=get_redis, send_email=notification_facade.send_email
)
app.state.shopping_session_factory = session_factory
app.add_middleware(SessionMiddleware, api_prefix=API_PREFIX)
app_dir = Path(__file__).parent
identity_dir = app_dir / "modules" / "identity"
register_templates("identity", identity_dir / "templates")
register_templates("ordering", app_dir / "modules" / "ordering" / "templates")
register_templates("catalog", app_dir / "modules" / "catalog" / "templates")

app.mount("/static/css", StaticFiles(directory=app_dir / "static" / "css"), name="static_css")
app.mount("/static/images", StaticFiles(directory=app_dir / "static" / "images"), name="static_images")
app.mount("/static/identity", StaticFiles(directory=identity_dir / "css"), name="identity_css")
app.include_router(identity_router)
app.include_router(ordering_router)
app.include_router(shopping_router)
register_error_handlers(app)


@app.get("/")
def root(request: Request):
    if "text/html" in request.headers.get("accept", ""):
        return storefront_home(request)
    return JSONResponse({"message": "Welcome to the Sobie Swimwear E-commerce API"}, headers={"Vary": "Accept"})
