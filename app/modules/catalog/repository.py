"""Truy vấn catalog; tên bảng chỉ lấy từ allowlist, giá trị dùng bind parameter."""
from sqlalchemy import text

KINDS = {"categories": "category", "collections": "collection", "genders": "gender", "colors": "color", "sizes": "size"}

async def rows(session, sql, params=None):
    result = await session.execute(text(sql), params or {})
    return [dict(row) for row in result.mappings()]

async def execute(session, sql, params=None):
    return await session.execute(text(sql), params or {})

async def taxonomy(session, table):
    return await rows(session, f"SELECT {table}_key AS key, {table}_name AS name FROM catalog.{table} ORDER BY {table}_name, {table}_key")

async def product(session, product_key, lock=False):
    found = await rows(session, "SELECT * FROM catalog.product WHERE product_key=:key" + (" FOR UPDATE" if lock else ""), {"key": product_key})
    return found[0] if found else None

async def variants(session, product_key):
    return await rows(session, """SELECT v.*, c.color_name, s.size_name FROM catalog.variant v
        JOIN catalog.color c ON c.color_key=v.variant_color_key
        JOIN catalog.size s ON s.size_key=v.variant_size_key
        WHERE variant_product_key=:key ORDER BY s.size_name, c.color_name, v.variant_id""", {"key": product_key})

async def gallery(session, product_key):
    return await rows(session, "SELECT * FROM catalog.gallery WHERE gallery_product_key=:key ORDER BY gallery_order_no", {"key": product_key})

async def collections(session, product_key):
    return await rows(session, "SELECT product_collection_collection_key AS key FROM catalog.product_collection WHERE product_collection_product_key=:key", {"key": product_key})

async def products(session, filters, staff=False):
    conditions, params = [], {}
    if not staff:
        conditions += ["p.product_status='ACTIVE'", "prices.min_price IS NOT NULL"]
    if filters.get("q"):
        params["q"] = "%" + filters["q"].replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        target = "p.product_id" if staff else "coalesce(p.product_description,'')"
        conditions.append(f"(unaccent(p.product_name) ILIKE unaccent(:q) OR unaccent({target}) ILIKE unaccent(:q))")
    for field in ("category", "gender"):
        if filters.get(field + "_key"):
            conditions.append(f"p.product_{field}_key=:{field}")
            params[field] = filters[field + "_key"]
    if filters.get("size_key"):
        conditions.append("EXISTS (SELECT 1 FROM catalog.variant sv WHERE sv.variant_product_key=p.product_key AND sv.variant_size_key=:size)")
        params["size"] = filters["size_key"]
    if filters.get("collection_key"):
        conditions.append("EXISTS (SELECT 1 FROM catalog.product_collection pc WHERE pc.product_collection_product_key=p.product_key AND pc.product_collection_collection_key=:collection)")
        params["collection"] = filters["collection_key"]
    if staff and filters.get("status"):
        conditions.append("p.product_status=:status")
        params["status"] = filters["status"]
    order = {"newest": "p.product_created_at DESC", "price_asc": "prices.min_price ASC", "price_desc": "prices.min_price DESC"}[filters.get("sort", "newest")]
    # shortcut: phân trang trong service sau truy vấn, chuyển COUNT/LIMIT sang SQL khi catalog lớn.
    return await rows(session, f"""SELECT p.*, c.category_name, g.gender_name, prices.min_price, prices.max_price,
        (SELECT gallery_url FROM catalog.gallery WHERE gallery_product_key=p.product_key AND gallery_order_no=1) AS image
        FROM catalog.product p
        JOIN catalog.category c ON c.category_key=p.product_category_key
        JOIN catalog.gender g ON g.gender_key=p.product_gender_key
        LEFT JOIN LATERAL (SELECT min(variant_sell_price) AS min_price, max(variant_sell_price) AS max_price
            FROM catalog.variant WHERE variant_product_key=p.product_key AND variant_status='ACTIVE' AND variant_sell_price>0) prices ON true
        WHERE {' AND '.join(conditions) or 'true'} ORDER BY {order}, p.product_id ASC""", params)

async def usage(session, table, item_key):
    if table in {"category", "gender"}:
        sql = f"SELECT product_key FROM catalog.product WHERE product_{table}_key=:key"
    elif table == "collection":
        sql = "SELECT product_collection_product_key FROM catalog.product_collection WHERE product_collection_collection_key=:key"
    else:
        sql = f"SELECT variant_product_key FROM catalog.variant WHERE variant_{table}_key=:key"
    return await rows(session, sql, {"key": item_key})
