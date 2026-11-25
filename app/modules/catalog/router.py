"""HTML endpoints C01–C21; route chỉ gọi service."""
import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import RedirectResponse

from app.shared.config.settings import Config
from app.shared.web.session import require_roles
from app.modules.identity.session import Role
from app.shared.web.rendering import templates
from . import service
from .schemas import CatalogError

router = APIRouter(prefix="/api/v1/catalog", tags=["catalog"])
logger = logging.getLogger(__name__)

async def employee(request: Request):
    if Config.CATALOG_DEMO:
        return
    await require_roles(Role.EMPLOYEE)(request)

def render(request, template, context=None, status=200):
    return templates.TemplateResponse(request, "catalog/" + template + ".html",
        {"base": "/api/v1/catalog", "demo": Config.CATALOG_DEMO, "notice": service.NOTICE, **(context or {})},
        status_code=status, headers={"Cache-Control": "private, no-cache", "Vary": "HX-Request"})

async def page(request, template, operation):
    try:
        return render(request, template, await operation)
    except CatalogError as exc:
        return render(request, "error", {"message": exc.message}, exc.status)
    except SQLAlchemyError:
        logger.exception("Catalog database read failed")
        return render(request, "error", {"message": "Không tải được sản phẩm, vui lòng thử lại"}, 503)

async def form_data(request):
    form = await request.form()
    if any(not isinstance(value, str) for _, value in form.multi_items()):
        raise CatalogError("Chỉ nhận trường văn bản; gallery nhận URL ảnh")
    # HTML demo và POST dùng cùng origin để tránh gửi form chéo website.
    origin = request.headers.get("origin")
    if origin and origin != f"{request.url.scheme}://{request.url.netloc}":
        raise CatalogError("Nguồn gửi form không hợp lệ", 403)
    return form

async def write(request, operation, destination, error_template=None, error_context=None):
    form = None
    try:
        form = await form_data(request)
        result = await operation(form)
        url = destination(result) if callable(destination) else destination
        return RedirectResponse(url + "?saved=1", status_code=303)
    except CatalogError as exc:
        context = {"message": exc.message, "submitted": list(form.multi_items()) if form else []}
        if error_template and form is not None:
            try:
                context.update(await error_context())
                context["form"] = form
                return render(request, error_template, context, exc.status)
            except (CatalogError, SQLAlchemyError):
                pass
        return render(request, "error", context, exc.status)
    except SQLAlchemyError:
        logger.exception("Catalog database write failed")
        return render(request, "error", {"message": "Không thể lưu dữ liệu, vui lòng thử lại."}, 503)

@router.get("/home", name="storefront_home")
async def home(request: Request):
    return await page(request, "home", service.home())

@router.get("/categories/{category_key}/products")
async def category(request: Request, category_key: str):
    return await page(request, "listing", service.listing(request.query_params, category_key=category_key))

@router.get("/search")
async def search(request: Request):
    if not request.query_params.get("q", "").strip():
        return render(request, "search", {"message": "Vui lòng nhập từ khóa"})
    return await page(request, "listing", service.listing(request.query_params))

@router.get("/products/{product_key}")
async def detail(request: Request, product_key: str):
    return await page(request, "detail", service.detail(product_key, True, request.query_params))

@router.get("/pages/{slug}")
async def info(request: Request, slug: str):
    pages = {"about": ("Giới thiệu", "Sobie Swimwear — đồ bơi."),
             "policies": ("Chính sách", "Nội dung chính sách chính thức chưa được cung cấp."),
             "faq": ("Câu hỏi thường gặp", "Chọn sản phẩm, chọn màu và size để xem giá. Giỏ hàng chưa tích hợp trong demo này.")}
    if slug not in pages:
        return render(request, "error", {"message": "Không tìm thấy trang"}, 404)
    return render(request, "info", {"title": pages[slug][0], "content": pages[slug][1]})

@router.get("/staff/products", dependencies=[Depends(employee)])
async def products(request: Request):
    return await page(request, "listing", service.listing(request.query_params, True))

@router.get("/staff/products/new", dependencies=[Depends(employee)])
async def new_product(request: Request):
    return await page(request, "edit", service.new_page())

@router.post("/staff/products/new", dependencies=[Depends(employee)])
async def create(request: Request):
    return await write(request, service.save_product, lambda key: f"/api/v1/catalog/staff/products/{key}/edit", "edit", service.new_page)

@router.get("/staff/products/{product_key}/edit", dependencies=[Depends(employee)])
async def edit(request: Request, product_key: str):
    return await page(request, "edit", service.detail(product_key))

@router.post("/staff/products/{product_key}/edit", dependencies=[Depends(employee)])
async def update(request: Request, product_key: str):
    return await write(request, lambda form: service.save_product(form, product_key),
        f"/api/v1/catalog/staff/products/{product_key}/edit", "edit", lambda: service.detail(product_key))

@router.post("/staff/products/{product_key}/status", dependencies=[Depends(employee)])
async def product_status(request: Request, product_key: str):
    return await write(request, lambda form: service.product_action(product_key, "status", form), f"/api/v1/catalog/staff/products/{product_key}/edit")

@router.post("/staff/products/{product_key}/delete", dependencies=[Depends(employee)])
async def delete(request: Request, product_key: str):
    return await write(request, lambda form: service.product_action(product_key, "delete", form), "/api/v1/catalog/staff/products")

@router.post("/staff/products/{product_key}/gallery", dependencies=[Depends(employee)])
async def gallery(request: Request, product_key: str):
    return await write(request, lambda form: service.product_action(product_key, "gallery", form), f"/api/v1/catalog/staff/products/{product_key}/edit")

@router.post("/staff/products/{product_key}/variants", dependencies=[Depends(employee)])
async def variants(request: Request, product_key: str):
    return await write(request, lambda form: service.product_action(product_key, "variants", form), f"/api/v1/catalog/staff/products/{product_key}/edit")

@router.post("/staff/products/{product_key}/variants/{variant_key}/delete", dependencies=[Depends(employee)])
async def variant_delete(request: Request, product_key: str, variant_key: str):
    return await write(request, lambda form: service.product_action(product_key, "variant-delete", form, variant_key), f"/api/v1/catalog/staff/products/{product_key}/edit")

@router.post("/staff/products/{product_key}/variants/{variant_key}/status", dependencies=[Depends(employee)])
async def variant_status(request: Request, product_key: str, variant_key: str):
    return await write(request, lambda form: service.product_action(product_key, "variant-status", form, variant_key), f"/api/v1/catalog/staff/products/{product_key}/edit")

@router.post("/staff/products/{product_key}/size-prices", dependencies=[Depends(employee)])
async def prices(request: Request, product_key: str):
    return await write(request, lambda form: service.product_action(product_key, "size-prices", form), f"/api/v1/catalog/staff/products/{product_key}/edit")

@router.get("/staff/taxonomy/{kind}", dependencies=[Depends(employee)])
async def taxonomy(request: Request, kind: str):
    return await page(request, "taxonomy", service.taxonomy_page(kind))

@router.post("/staff/taxonomy/{kind}", dependencies=[Depends(employee)])
async def taxonomy_create(request: Request, kind: str):
    return await write(request, lambda form: service.taxonomy_write(kind, "new", form), f"/api/v1/catalog/staff/taxonomy/{kind}")

@router.post("/staff/taxonomy/{kind}/{key}/edit", dependencies=[Depends(employee)])
async def taxonomy_edit(request: Request, kind: str, key: str):
    return await write(request, lambda form: service.taxonomy_write(kind, "edit", form, key), f"/api/v1/catalog/staff/taxonomy/{kind}")

@router.post("/staff/taxonomy/{kind}/{key}/delete", dependencies=[Depends(employee)])
async def taxonomy_delete(request: Request, kind: str, key: str):
    return await write(request, lambda form: service.taxonomy_write(kind, "delete", form, key), f"/api/v1/catalog/staff/taxonomy/{kind}")
