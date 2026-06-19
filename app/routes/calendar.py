"""
Calendar route — monthly grid view.

Endpoints:
  GET /calendar            → Current month
  GET /calendar?year=&month= → Specific month
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.views.monthly import build_month_view

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/calendar", response_class=HTMLResponse)
async def calendar_page(
    request: Request,
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
):
    """Monthly calendar view with tithi and festival overlays."""
    today = date.today()

    if year is None:
        year = today.year
    if month is None:
        month = today.month

    data = build_month_view(year, month)
    return templates.TemplateResponse(
        request,
        "calendar.html",
        {
            "data": data,
            "prev_month": _prev_month(year, month),
            "next_month": _next_month(year, month),
        },
    )


# ---------- Navigation helpers ----------

def _prev_month(year: int, month: int) -> dict:
    """Return {year, month} for the previous month."""
    if month == 1:
        return {"year": year - 1, "month": 12}
    return {"year": year, "month": month - 1}


def _next_month(year: int, month: int) -> dict:
    """Return {year, month} for the next month."""
    if month == 12:
        return {"year": year + 1, "month": 1}
    return {"year": year, "month": month + 1}
