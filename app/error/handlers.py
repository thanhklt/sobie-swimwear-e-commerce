"""Chuyển ngoại lệ thành response HTML cho trình duyệt và HTMX.

- Trang thường: 401 có login_route thì chuyển hướng 303 tới trang đăng nhập; còn lại render
  trang lỗi, giữ mã 401 / 403, không cache.
- Request HTMX: 401 có login_route thì trả HX-Redirect; còn lại trả HX-Refresh để trình duyệt
  tải lại cả trang (HTMX mặc định không chèn nội dung response 4xx).
"""

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import NoMatchFound

from app.error.exceptions import SessionAccessError
from app.modules.identity.session import SessionPortal
from app.shared.web.rendering import templates

# [GD] Tên route; module identity (UC-02) và trang chủ (UC-09) đặt đúng các tên này.
LOGIN_ROUTES = {
    SessionPortal.STOREFRONT: "storefront_login",
    SessionPortal.PORTAL: "portal_login",
}
HOME_ROUTES = {
    SessionPortal.STOREFRONT: "storefront_home",
    SessionPortal.PORTAL: "portal_home",
}

# Phản hồi gắn với phiên đăng nhập không được cache (BR-GIAIDOAN1, Cache).
_NO_STORE = {"Cache-Control": "no-store", "Vary": "HX-Request"}

_PAGES = {
    401: (
        "Bạn cần đăng nhập",
        "Phiên đăng nhập đã hết hạn hoặc bạn chưa đăng nhập.",
        LOGIN_ROUTES,
        "Đăng nhập",
    ),
    403: (
        "Không có quyền truy cập",
        "Tài khoản của bạn không được phép xem trang này.",
        HOME_ROUTES,
        "Về trang chủ",
    ),
}


def _path_for(request: Request, route_name: str) -> str | None:
    """Đường dẫn của route theo tên; route chưa đăng ký thì trả None."""
    try:
        return request.url_for(route_name).path
    except NoMatchFound:
        return None


async def session_access_error(request: Request, exc: SessionAccessError) -> Response:
    login_path = _path_for(request, exc.login_route) if exc.login_route else None
    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:
        header = {"HX-Redirect": login_path} if login_path else {"HX-Refresh": "true"}
        return Response(status_code=exc.status_code, headers=header | _NO_STORE)

    if login_path:
        return RedirectResponse(login_path, status_code=303, headers=_NO_STORE)

    title, message, link_routes, link_label = _PAGES[exc.status_code]
    portal = getattr(request.state, "auth_portal", SessionPortal.STOREFRONT)
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "title": title,
            "message": message,
            "link_path": _path_for(request, link_routes[portal]),
            "link_label": link_label,
        },
        status_code=exc.status_code,
        headers=_NO_STORE,
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(SessionAccessError, session_access_error)
