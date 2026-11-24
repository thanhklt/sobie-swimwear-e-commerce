"""Tầng Route của module reporting: kiểm tra bộ lọc và trả dashboard HTML."""

from datetime import date, datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.error.handlers import LOGIN_ROUTES
from app.modules.identity.session import Role, SessionPortal
from app.modules.reporting import service
from app.modules.reporting.schemas import ReportPeriod
from app.shared.web.rendering import templates
from app.shared.web.session import PORTAL_PREFIX, require_roles

router = APIRouter(prefix=PORTAL_PREFIX)
_HEADERS = {"Cache-Control": "no-store", "Vary": "HX-Request"}
_DATE_ERROR = (
    "Ngày bắt đầu phải nhỏ hơn ngày kết thúc. Nhập ngày theo định dạng dd/mm/yyyy."
)


def _parse_date(value: str) -> date:
    value = value.strip()
    if "/" in value:
        return datetime.strptime(value, "%d/%m/%Y").date()
    return date.fromisoformat(value)


def _parse_period(start: str | None, end: str | None) -> ReportPeriod:
    if start is None or end is None:
        raise ValueError(_DATE_ERROR)
    start_date, end_date = _parse_date(start), _parse_date(end)
    if start_date >= end_date or end_date == date.max:
        raise ValueError(_DATE_ERROR)
    period = ReportPeriod(start_date, end_date)
    period.utc_bounds()
    return period


@router.get(
    "/dashboard",
    name="reporting_dashboard",
    response_class=HTMLResponse,
    dependencies=[
        Depends(
            require_roles(Role.EMPLOYEE, login_route=LOGIN_ROUTES[SessionPortal.PORTAL])
        )
    ],
)
async def dashboard(
    request: Request,
    start_date: str | None = None,
    end_date: str | None = None,
    previous_start_date: str | None = None,
    previous_end_date: str | None = None,
) -> HTMLResponse:
    is_htmx = request.headers.get("HX-Request") == "true"
    date_error = None

    if start_date is None and end_date is None:
        period = ReportPeriod.current_month()
    else:
        try:
            period = _parse_period(start_date, end_date)
        except (ValueError, OverflowError):
            date_error = _DATE_ERROR
            if is_htmx:
                return templates.TemplateResponse(
                    request,
                    "reporting/_date_error.html",
                    {"date_error": date_error},
                    headers=_HEADERS
                    | {"HX-Retarget": "#dashboard-errors", "HX-Reswap": "innerHTML"},
                )
            try:
                period = _parse_period(previous_start_date, previous_end_date)
            except (ValueError, OverflowError):
                period = ReportPeriod.current_month()

    return templates.TemplateResponse(
        request,
        "reporting/_dashboard.html" if is_htmx else "reporting/dashboard.html",
        {
            "dashboard": await service.get_dashboard(period),
            "period": period,
            "form_start_date": (start_date or "")
            if date_error
            else period.start_date.strftime("%d/%m/%Y"),
            "form_end_date": (end_date or "")
            if date_error
            else period.end_date.strftime("%d/%m/%Y"),
            "date_error": date_error,
            "order_status_labels": service.ORDER_STATUS_LABELS,
        },
        headers=_HEADERS,
    )
