"""Tầng Route shopping — UI thử SSR (/dev/shopping).

Router chỉ validate input / gọi service / render Jinja. Không gọi repository.
Adapter seed [GD] cung cấp account demo, giá, tồn, sản phẩm cho đến khi
identity/catalog/inventory có service công khai.
"""

from __future__ import annotations

import json
from typing import Annotated
from uuid import UUID

from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.shopping import adapters, service
from app.modules.shopping.adapters import DEMO_EMAIL
from app.modules.shopping.exceptions import ShoppingError
from app.modules.shopping.schemas import GuestCartLine
from app.shared.database.engine import session_factory
from app.shared.web.rendering import templates

router = APIRouter(prefix="/dev/shopping", tags=["shopping-dev"])


async def get_db() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]


def _redirect(path: str, *, ok: str | None = None, error: str | None = None) -> RedirectResponse:
    from urllib.parse import urlencode

    params = {}
    if ok:
        params["ok"] = ok
    if error:
        params["error"] = error
    qs = f"?{urlencode(params)}" if params else ""
    return RedirectResponse(f"{path}{qs}", status_code=303)


def _flash(request: Request) -> dict[str, str | None]:
    return {
        "flash_ok": request.query_params.get("ok"),
        "flash_error": request.query_params.get("error"),
    }


@router.get("")
async def shopping_home(request: Request):
    return templates.TemplateResponse(
        request,
        "shopping_home.html",
        {
            "title": "Thử shopping",
            "demo_email": DEMO_EMAIL,
            **_flash(request),
        },
    )


@router.get("/cart")
async def cart_page(request: Request, db: DbSession):
    account_key = await adapters.get_demo_account_key(db)
    availability = adapters.SeedAvailability(db)
    pricing = adapters.SeedPricing(db)
    cart = await service.get_cart(
        db,
        account_key=account_key,
        availability=availability,
        pricing=pricing,
    )
    variants = await adapters.list_seed_variants(db)
    labels = await adapters.variant_labels(
        db, [line.variant_key for line in cart.lines]
    )
    sample_variant = (
        str(variants[0]["variant_key"]) if variants else ""
    )
    clear_guest = bool(
        request.query_params.get("ok")
        and "Gộp" in (request.query_params.get("ok") or "")
    )
    return templates.TemplateResponse(
        request,
        "shopping_cart.html",
        {
            "title": "Giỏ hàng",
            "demo_email": DEMO_EMAIL,
            "cart": cart,
            "variants": variants,
            "labels": labels,
            "sample_variant_key": sample_variant,
            "clear_guest_storage": clear_guest,
            **_flash(request),
        },
    )


@router.post("/cart/add")
async def cart_add(
    db: DbSession,
    variant_key: Annotated[UUID, Form()],
    quantity: Annotated[int, Form()],
):
    try:
        account_key = await adapters.get_demo_account_key(db)
        await service.add_item_to_cart(
            db,
            account_key=account_key,
            variant_key=variant_key,
            quantity=quantity,
            availability=adapters.SeedAvailability(db),
        )
        return _redirect("/dev/shopping/cart", ok="Đã thêm vào giỏ")
    except ShoppingError as exc:
        return _redirect("/dev/shopping/cart", error=exc.message)


@router.post("/cart/set-qty")
async def cart_set_qty(
    db: DbSession,
    variant_key: Annotated[UUID, Form()],
    quantity: Annotated[int, Form()],
):
    try:
        account_key = await adapters.get_demo_account_key(db)
        await service.set_cart_item_quantity(
            db,
            account_key=account_key,
            variant_key=variant_key,
            quantity=quantity,
            availability=adapters.SeedAvailability(db),
        )
        return _redirect("/dev/shopping/cart", ok="Đã cập nhật số lượng")
    except ShoppingError as exc:
        return _redirect("/dev/shopping/cart", error=exc.message)


@router.post("/cart/remove")
async def cart_remove(
    db: DbSession,
    variant_key: Annotated[UUID, Form()],
):
    try:
        account_key = await adapters.get_demo_account_key(db)
        await service.remove_cart_item(
            db, account_key=account_key, variant_key=variant_key
        )
        return _redirect("/dev/shopping/cart", ok="Đã xóa dòng giỏ")
    except ShoppingError as exc:
        return _redirect("/dev/shopping/cart", error=exc.message)


@router.post("/cart/merge")
async def cart_merge(
    db: DbSession,
    merge_id: Annotated[str, Form()],
    guest_json: Annotated[str, Form()],
):
    try:
        raw = json.loads(guest_json)
        guest_lines = [
            GuestCartLine(
                variant_key=UUID(str(item["variant_key"])),
                quantity=int(item["quantity"]),
            )
            for item in raw
        ]
        account_key = await adapters.get_demo_account_key(db)
        await service.merge_guest_cart(
            db,
            account_key=account_key,
            merge_id=merge_id,
            guest_lines=guest_lines,
            availability=adapters.SeedAvailability(db),
        )
        return _redirect(
            "/dev/shopping/cart",
            ok="Gộp giỏ thành công — localStorage guest sẽ được xóa",
        )
    except (ShoppingError, json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
        message = exc.message if isinstance(exc, ShoppingError) else "Dữ liệu gộp không hợp lệ"
        return _redirect("/dev/shopping/cart", error=message)


@router.get("/wishlist")
async def wishlist_page(request: Request, db: DbSession):
    account_key = await adapters.get_demo_account_key(db)
    catalog = adapters.SeedProductCatalog(db)
    wishlist = await service.get_wishlist(
        db, account_key=account_key, catalog=catalog
    )
    products = await adapters.list_seed_products(db)
    return templates.TemplateResponse(
        request,
        "shopping_wishlist.html",
        {
            "title": "Wishlist",
            "demo_email": DEMO_EMAIL,
            "wishlist": wishlist,
            "products": products,
            **_flash(request),
        },
    )


@router.post("/wishlist/add")
async def wishlist_add(
    db: DbSession,
    product_key: Annotated[UUID, Form()],
):
    try:
        account_key = await adapters.get_demo_account_key(db)
        added = await service.add_to_wishlist(
            db,
            account_key=account_key,
            product_key=product_key,
            catalog=adapters.SeedProductCatalog(db),
        )
        msg = "Đã thả tim" if added else "Sản phẩm đã có trong wishlist"
        return _redirect("/dev/shopping/wishlist", ok=msg)
    except ShoppingError as exc:
        return _redirect("/dev/shopping/wishlist", error=exc.message)


@router.post("/wishlist/remove")
async def wishlist_remove(
    db: DbSession,
    product_key: Annotated[UUID, Form()],
):
    try:
        account_key = await adapters.get_demo_account_key(db)
        await service.remove_from_wishlist(
            db, account_key=account_key, product_key=product_key
        )
        return _redirect("/dev/shopping/wishlist", ok="Đã bỏ tim")
    except ShoppingError as exc:
        return _redirect("/dev/shopping/wishlist", error=exc.message)
