"""Envelope response thống nhất cho mọi API: success, data, error, meta
(meta.timestamp, meta.request_id, meta.pagination) theo AGENTS.md.
"""

from datetime import UTC, datetime
from uuid import uuid4

from starlette.requests import Request
from starlette.responses import JSONResponse


def error_response(
    request: Request, *, status_code: int, code: str, message: str
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None) or f"req_{uuid4().hex}"
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "error": {"code": code, "message": message, "details": None},
            "meta": {
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "request_id": request_id,
            },
        },
    )
