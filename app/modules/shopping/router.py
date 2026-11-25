"""Tầng Route của module shopping: nhận request, kiểm tra dữ liệu đầu vào, gọi service,
trả response.
Không gọi repository hoặc database trực tiếp. Chưa triển khai.
"""

import re
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.modules.identity.session import AuthenticatedSession, Role
from app.modules.shopping.service import CartMergeConflict, merge_guest_cart
from app.security.session import require_roles

cart_merge_path = "/api/v1/shopping/cart/merge"
router = APIRouter()
Customer = Annotated[AuthenticatedSession, Depends(require_roles(Role.CUSTOMER))]
_NO_STORE = {"Cache-Control": "no-store"}


@router.post(cart_merge_path)
async def cart_merge(request: Request, actor: Customer) -> JSONResponse:
    async with request.form() as form:
        try:
            [merge_key] = form.getlist("merge_key")
            merge_key = UUID(str(merge_key))
            variants, quantities = form.getlist("variant_key"), form.getlist("quantity")
            if not variants or len(variants) != len(quantities):
                raise ValueError
            items: dict[UUID, int] = {}
            for variant, quantity in zip(variants, quantities):
                variant_key = UUID(str(variant))
                if not isinstance(quantity, str) or not re.fullmatch(r"[0-9]{1,10}", quantity):
                    raise ValueError
                count = int(quantity)
                if not 0 < count <= 2_147_483_647:
                    raise ValueError
                items[variant_key] = items.get(variant_key, 0) + count
        except ValueError:
            return JSONResponse({"message": "Dữ liệu giỏ hàng không hợp lệ."}, 400, headers=_NO_STORE)
    try:
        result = await merge_guest_cart(
            request.app.state.shopping_session_factory, actor.account_key, merge_key, items
        )
    except CartMergeConflict:
        return JSONResponse({"message": "Khóa gộp đã được dùng cho một giỏ khác."}, 409, headers=_NO_STORE)
    return JSONResponse(result, headers=_NO_STORE)
