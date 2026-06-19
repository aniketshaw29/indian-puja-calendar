"""
Daily page routes — the main landing experience.

Endpoints:
  GET /           → Today's panchang + muhurtas + festivals
  GET /day?date=  → Same view for a specific date
"""

from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import DEFAULT_LOCATION
from app.views.daily import build_daily_view

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _build_timeline_context(data, d):
    """
    Compute timeline segment positions and time strings for the template.

    Each muhurta gets a left% and width% relative to the sunrise→sunset window.
    Returns a dict with:
      - timeline_segments: list of {name, category, left, width, start, end}
      - sunrise_str, sunset_str, day_length_str
      - sunrise_str_short, sunset_str_short
      - now_percent, now_str
      - prev_date, next_date (as ISO strings)
    """
    ctx = {}
    panch = data.panchanga

    # Previous/next date navigation.
    ctx["prev_date"] = (d - timedelta(days=1)).isoformat()
    ctx["next_date"] = (d + timedelta(days=1)).isoformat()

    # Sunrise/sunset display strings.
    if panch.sunrise and panch.sunset:
        ctx["sunrise_str"] = panch.sunrise.strftime("%I:%M %p")
        ctx["sunset_str"] = panch.sunset.strftime("%I:%M %p")
        ctx["sunrise_str_short"] = panch.sunrise.strftime("%I:%M%p").lstrip("0")
        ctx["sunset_str_short"] = panch.sunset.strftime("%I:%M%p").lstrip("0")

        # Day length.
        day_secs = (panch.sunset - panch.sunrise).total_seconds()
        hours = int(day_secs // 3600)
        mins = int((day_secs % 3600) // 60)
        ctx["day_length_str"] = f"{hours}h {mins}m"

        # Compute timeline segments as percentages.
        total_span = (panch.sunset - panch.sunrise).total_seconds()
        segments = []
        for m in data.muhurtas:
            m_start = m.starts_at
            m_end = m.ends_at

            # Clamp to the visible day window.
            seg_left_start = max(m_start, panch.sunrise)
            seg_left_end = min(m_end, panch.sunset)

            if seg_left_end <= seg_left_start:
                continue

            left_pct = (seg_left_start - panch.sunrise).total_seconds() / total_span * 100
            width_pct = (seg_left_end - seg_left_start).total_seconds() / total_span * 100

            segments.append({
                "name": m.name,
                "category": m.category,
                "left": round(left_pct, 1),
                "width": round(width_pct, 1),
                "start": m_start.strftime("%I:%M %p").lstrip("0"),
                "end": m_end.strftime("%I:%M %p").lstrip("0"),
            })
        ctx["timeline_segments"] = segments

        # Current time marker position.
        now = datetime.now(panch.sunrise.tzinfo)
        ctx["now_str"] = now.strftime("%I:%M %p").lstrip("0")
        if now < panch.sunrise:
            ctx["now_percent"] = 0
        elif now > panch.sunset:
            ctx["now_percent"] = 100
        else:
            ctx["now_percent"] = round(
                (now - panch.sunrise).total_seconds() / total_span * 100, 1
            )
    else:
        ctx["sunrise_str"] = "--"
        ctx["sunset_str"] = "--"
        ctx["day_length_str"] = "--"
        ctx["sunrise_str_short"] = "--"
        ctx["sunset_str_short"] = "--"
        ctx["timeline_segments"] = []
        ctx["now_percent"] = 0
        ctx["now_str"] = "--"

    return ctx


@router.get("/", response_class=HTMLResponse)
async def today_page(request: Request):
    """Today's full panchang view with muhurtas and festivals."""
    d = date.today()
    data = build_daily_view(d)
    ctx = _build_timeline_context(data, d)
    ctx.update({"data": data, "view_date": d.isoformat()})
    return templates.TemplateResponse(request, "today.html", ctx)


@router.get("/day", response_class=HTMLResponse)
async def day_page(
    request: Request,
    date_str: Optional[str] = Query(None, alias="date"),
):
    """
    Detailed panchang for a specific date.

    Accepts 'date' query param in YYYY-MM-DD format.
    Defaults to today if omitted.
    """
    if date_str:
        try:
            d = date.fromisoformat(date_str)
        except ValueError:
            d = date.today()
    else:
        d = date.today()

    data = build_daily_view(d)
    ctx = _build_timeline_context(data, d)
    ctx.update({"data": data, "view_date": d.isoformat()})
    return templates.TemplateResponse(request, "today.html", ctx)
