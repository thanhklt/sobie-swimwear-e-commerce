"""Ngoại lệ dùng chung cho các route."""


class SessionAccessError(Exception):
    """Request không có phiên hợp lệ (401) hoặc sai vai trò (403)."""

    def __init__(self, *, status_code: int, login_route: str | None = None):
        super().__init__(status_code)
        self.status_code = status_code
        self.login_route = login_route
