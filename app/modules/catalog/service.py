"""Nghiệp vụ catalog và transaction; không truy cập dữ liệu module khác."""
from contextlib import asynccontextmanager
from math import ceil

from sqlalchemy.exc import IntegrityError
from app.shared.database.engine import session_factory
from app.shared.database.transaction import transaction
from . import repository as repo
from .schemas import CatalogError, key, name, status, image_url, price

UNAVAILABLE = "Chưa hỗ trợ trong phạm vi demo: cần service inventory/ordering/promotion để kiểm tra ràng buộc."
NOTICE = "Demo catalog: chưa tích hợp tồn kho, khuyến mãi, bán chạy, giỏ hàng và yêu thích."

@asynccontextmanager
async def unit():
    try:
        async with session_factory() as session:
            async with transaction(session):
                yield session
    except IntegrityError:
        raise CatalogError("Dữ liệu trùng hoặc đang được sử dụng; không có thay đổi nào được lưu.", 409) from None

def kind_table(kind):
    if kind not in repo.KINDS:
        raise CatalogError("Không tìm thấy loại phân loại", 404)
    return repo.KINDS[kind]

async def taxonomies(session):
    return {kind: await repo.taxonomy(session, table) for kind, table in repo.KINDS.items()}

async def existing(session, product_key, lock=False):
    item = await repo.product(session, key(product_key), lock)
    if not item:
        raise CatalogError("Không tìm thấy sản phẩm", 404)
    return item

async def require_editable(session, product_key):
    # Không thể chứng minh chưa nhập CONFIRMED khi inventory chưa có service.
    if await repo.variants(session, product_key):
        raise CatalogError(UNAVAILABLE, 503)

async def taxonomy_page(kind):
    table = kind_table(kind)
    async with unit() as session:
        return {"kind": kind, "items": await repo.taxonomy(session, table)}

async def taxonomy_write(kind, action, form, item_key=None):
    table = kind_table(kind)
    item_key = key(item_key) if item_key else None
    value = name(form.get("name", ""), 255 if table in {"category", "collection"} else 50, True) if action != "delete" else None
    if action == "delete" and form.get("confirm") != "yes":
        raise CatalogError("Cần xác nhận xóa")
    async with unit() as session:
        # Serialize tên trong cùng loại; không khóa toàn bộ Catalog.
        await repo.execute(session, "SELECT pg_advisory_xact_lock(hashtextextended(:scope, 0))", {"scope": "catalog.name." + table})
        if item_key:
            found = await repo.rows(session, f"SELECT * FROM catalog.{table} WHERE {table}_key=:key FOR UPDATE", {"key": item_key})
            if not found:
                raise CatalogError("Không tìm thấy mục", 404)
            used = await repo.usage(session, table, item_key)
            if action == "delete" and used:
                raise CatalogError(f"Đang có {len(used)} liên kết sử dụng, không thể xóa", 409)
            if action == "edit":
                for product_key in sorted({str(next(iter(row.values()))) for row in used}):
                    await existing(session, product_key, True)
                    await require_editable(session, product_key)
        if value:
            duplicate = await repo.rows(session, f"SELECT {table}_key FROM catalog.{table} WHERE lower({table}_name)=lower(:name) AND (CAST(:key AS uuid) IS NULL OR {table}_key != CAST(:key AS uuid))", {"name": value, "key": item_key})
            if duplicate:
                raise CatalogError("Tên đã tồn tại", 409)
        if action == "new":
            await repo.execute(session, f"INSERT INTO catalog.{table} ({table}_name) VALUES (:name)", {"name": value})
        elif action == "edit":
            await repo.execute(session, f"UPDATE catalog.{table} SET {table}_name=:name WHERE {table}_key=:key", {"name": value, "key": item_key})
        else:
            await repo.execute(session, f"DELETE FROM catalog.{table} WHERE {table}_key=:key", {"key": item_key})

async def listing(query, staff=False, category_key=None):
    filters = dict(query)
    filters["q"] = filters.get("q", "").strip()[:100]
    filters["sort"] = filters.get("sort", "newest")
    if filters["sort"] not in {"newest", "price_asc", "price_desc"}:
        raise CatalogError("Sắp xếp không hợp lệ")
    if filters.get("status"):
        status(filters["status"])
    try:
        page = max(1, int(filters.get("page", "1")))
    except ValueError:
        raise CatalogError("Trang phải là số nguyên") from None
    async with unit() as session:
        taxa = await taxonomies(session)
        if category_key:
            category_key = key(category_key)
            if category_key not in {str(row["key"]) for row in taxa["categories"]}:
                raise CatalogError("Không tìm thấy danh mục", 404)
            filters["category_key"] = category_key
        for field, kind in (("category", "categories"), ("gender", "genders"), ("size", "sizes"), ("collection", "collections")):
            value = filters.get(field + "_key")
            if value and value not in {str(row["key"]) for row in taxa[kind]}:
                filters.pop(field + "_key", None)
        items = await repo.products(session, filters, staff)
        count = len(items)
        pages = ceil(count / (20 if staff else 12))
        page = min(page, pages) if pages else 1
        size = 20 if staff else 12
        return {"items": items[(page-1)*size:page*size], "filters": filters, "taxa": taxa, "total": count, "pages": pages, "page": page, "staff": staff}

async def home():
    async with unit() as session:
        taxa = await taxonomies(session)
        items = await repo.products(session, {"sort": "newest"})
        groups = []
        for collection in taxa["collections"]:
            selected = await repo.products(session, {"sort": "newest", "collection_key": str(collection["key"])})
            if selected:
                groups.append({"name": collection["name"], "items": selected[:4]})
        return {"items": items[:8], "groups": groups, "taxa": taxa}

async def detail(product_key, public=False, query=None):
    async with unit() as session:
        product = await existing(session, product_key)
        if public and product["product_status"] != "ACTIVE":
            raise CatalogError("Không tìm thấy sản phẩm", 404)
        variants = await repo.variants(session, product_key)
        gallery = await repo.gallery(session, product_key)
        eligible = [v for v in variants if v["variant_status"] == "ACTIVE" and v["variant_sell_price"] and v["variant_sell_price"] > 0]
        selected = dict(query or {})
        for field in ("color_key", "size_key"):
            if selected.get(field):
                selected[field] = key(selected[field])
        valid_prices = [v["variant_sell_price"] for v in eligible if not selected.get("size_key") or str(v["variant_size_key"]) == selected["size_key"]]
        return {"product": product, "variants": variants, "gallery": gallery, "eligible": eligible,
                "min_price": min(valid_prices) if valid_prices else None, "max_price": max(valid_prices) if valid_prices else None,
                "selected": selected, "taxa": await taxonomies(session),
                "collection_keys": [str(v["key"]) for v in await repo.collections(session, product_key)],
                "locked": bool(variants)}

async def new_page():
    async with unit() as session:
        return {"taxa": await taxonomies(session), "product": None, "collection_keys": [], "locked": False}

async def references(session, category_key, gender_key, collection_keys):
    selected = {"category": [category_key], "gender": [gender_key], "collection": collection_keys}
    for table in sorted(selected):
        for item_key in sorted(set(selected[table])):
            found = await repo.rows(session, f"SELECT {table}_key FROM catalog.{table} WHERE {table}_key=:key FOR KEY SHARE", {"key": item_key})
            if not found:
                raise CatalogError("Phân loại không còn tồn tại, vui lòng tải lại form", 409)

async def save_product(form, product_key=None):
    value = name(form.get("name", ""))
    category_key, gender_key = key(form.get("category_key")), key(form.get("gender_key"))
    collection_keys = [key(v) for v in form.getlist("collection_key")]
    urls = [image_url(v) for v in form.getlist("image_url") if v.strip()] if not product_key else []
    async with unit() as session:
        await references(session, category_key, gender_key, collection_keys)
        if product_key:
            product = await existing(session, product_key, True)
            current_collections = {str(v["key"]) for v in await repo.collections(session, product_key)}
            changed = (value != product["product_name"] or category_key != str(product["product_category_key"])
                       or gender_key != str(product["product_gender_key"]) or set(collection_keys) != current_collections)
            if changed:
                await require_editable(session, product_key)
            else:
                await repo.execute(session, "UPDATE catalog.product SET product_description=:description, product_updated_at=now() WHERE product_key=:key", {"description": form.get("description", ""), "key": product_key})
                return str(product_key)
        await repo.execute(session, "SELECT pg_advisory_xact_lock(hashtextextended('catalog.name.product', 0))")
        duplicates = await repo.rows(session, "SELECT product_key FROM catalog.product WHERE lower(trim(product_name))=lower(:name) AND (CAST(:key AS uuid) IS NULL OR product_key != CAST(:key AS uuid))", {"name": value, "key": product_key})
        if duplicates:
            raise CatalogError("Tên sản phẩm đã tồn tại", 409)
        params = {"name": value, "description": form.get("description", ""), "category": category_key, "gender": gender_key, "key": product_key}
        if product_key:
            await repo.execute(session, """UPDATE catalog.product SET product_name=:name, product_description=:description,
                product_category_key=:category, product_gender_key=:gender, product_updated_at=now() WHERE product_key=:key""", params)
            await repo.execute(session, "DELETE FROM catalog.product_collection WHERE product_collection_product_key=:key", params)
        else:
            # Khóa cấp mã riêng, không tái sử dụng mã đã xóa.
            await repo.execute(session, "SELECT pg_advisory_xact_lock(hashtextextended('catalog.product.code', 0))")
            codes = await repo.rows(session, "SELECT coalesce(max(substring(product_id from 4)::int),0)+1 AS code FROM catalog.product")
            code = codes[0]["code"]
            if code > 9999:
                raise CatalogError("Đã hết dải mã sản phẩm", 409)
            params["code"] = f"SP-{code:04d}"
            created = await repo.rows(session, """INSERT INTO catalog.product(product_id, product_name, product_description, product_category_key, product_gender_key)
                VALUES (:code,:name,:description,:category,:gender) RETURNING product_key""", params)
            product_key = str(created[0]["product_key"])
        for collection_key in set(collection_keys):
            await repo.execute(session, "INSERT INTO catalog.product_collection VALUES (:key,:collection)", {"key": product_key, "collection": collection_key})
        for order, url in enumerate(urls, 1):
            await repo.execute(session, "INSERT INTO catalog.gallery(gallery_product_key,gallery_order_no,gallery_url) VALUES (:key,:order,:url)", {"key": product_key, "order": order, "url": url})
        return str(product_key)

async def product_action(product_key, action, form, variant_key=None):
    async with unit() as session:
        product = await existing(session, product_key, True)
        if action == "delete":
            if form.get("confirm") != "yes":
                raise CatalogError("Cần xác nhận xóa")
            raise CatalogError(UNAVAILABLE, 503)
        if variant_key:
            variant_key = key(variant_key)
            variants = await repo.variants(session, product_key)
            if variant_key not in {str(v["variant_key"]) for v in variants}:
                raise CatalogError("Không tìm thấy biến thể thuộc sản phẩm", 404)
        if action == "variants":
            if not form.getlist("color_key") or not form.getlist("size_key"):
                raise CatalogError("Vui lòng chọn màu và size")
            for value in form.getlist("color_key") + form.getlist("size_key"):
                key(value)
            raise CatalogError("Chưa hỗ trợ tạo biến thể: cần inventory tạo tồn kho trong cùng transaction.", 503)
        if action == "size-prices":
            sizes, prices = form.getlist("size_key"), form.getlist("sell_price")
            if not sizes or len(sizes) != len(prices) or len(set(sizes)) != len(sizes):
                raise CatalogError("Danh sách size/giá không hợp lệ")
            for size_key, value in zip(sizes, prices):
                key(size_key)
                if value.strip():
                    price(value)
            raise CatalogError(UNAVAILABLE, 503)
        if action == "variant-status":
            status(form.get("status", ""))
            raise CatalogError(UNAVAILABLE, 503)
        if action == "variant-delete":
            if form.get("confirm") != "yes":
                raise CatalogError("Cần xác nhận xóa")
            raise CatalogError(UNAVAILABLE, 503)
        await require_editable(session, product_key)
        if action == "status":
            value = status(form.get("status", ""))
            if value == "ACTIVE":
                raise CatalogError("Cần ít nhất một biến thể, giá theo size và ảnh trước khi mở bán", 409)
            await repo.execute(session, "UPDATE catalog.product SET product_status=:status, product_updated_at=now() WHERE product_key=:key", {"key": product_key, "status": value})
        elif action == "gallery":
            urls = form.getlist("image_url")
            orders = form.getlist("order_no")
            if len(urls) != len(orders):
                raise CatalogError("Thiếu thứ tự ảnh")
            images = []
            for url, order in zip(urls, orders):
                if not url.strip():
                    continue
                if not order.isascii() or not order.isdigit() or not 1 <= int(order) <= 2147483647:
                    raise CatalogError("Thứ tự ảnh phải là số nguyên dương")
                images.append((int(order), image_url(url)))
            if len({v[0] for v in images}) != len(images) or sorted(v[0] for v in images) != list(range(1, len(images)+1)):
                raise CatalogError("Thứ tự ảnh phải liên tiếp từ 1, không trùng")
            if product["product_status"] == "ACTIVE" and not images:
                raise CatalogError("Không thể xóa ảnh cuối cùng khi đang bán", 409)
            await repo.execute(session, "DELETE FROM catalog.gallery WHERE gallery_product_key=:key", {"key": product_key})
            for order, url in images:
                await repo.execute(session, "INSERT INTO catalog.gallery(gallery_product_key,gallery_order_no,gallery_url) VALUES (:key,:order,:url)", {"key": product_key, "order": order, "url": url})
