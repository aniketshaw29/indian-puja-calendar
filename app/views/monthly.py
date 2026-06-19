"""
Monthly calendar view: builds a grid of days with tithi and festival overlays.

Each day cell contains the tithi name and any festivals active on that date.
This view iterates through all days of a Gregorian month and delegates
per-day computation to the daily view builder.
"""

import calendar
import logging
from datetime import date, timedelta

from app.config import DEFAULT_LOCATION
from app.models import CalendarDay, MonthViewData

logger = logging.getLogger(__name__)


def build_month_view(
    year: int,
    month: int,
    lat: float = DEFAULT_LOCATION.latitude,
    lon: float = DEFAULT_LOCATION.longitude,
) -> MonthViewData:
    """
    Build a calendar grid for the given month.

    Steps:
      1. Determine the first day and number of days in the month.
      2. Compute which days from the previous/next month appear as filler.
      3. For each day in the grid, compute tithi and festival data.

    In a grid that starts on a Sunday (calendar.firstweekday = 6 would be
    Sunday-first for some regions), but for a standard Monday-first grid
    we use the default calendar module behaviour.
    """
    today = date.today()
    month_names = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]

    # Step 1: Month bounds.
    first_weekday, num_days = calendar.monthrange(year, month)
    # first_weekday: Monday=0 … Sunday=6

    # Step 2: Build leading filler days from previous month.
    days: list[CalendarDay] = []
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    _, prev_num_days = calendar.monthrange(prev_year, prev_month)

    # Padding before the first day.
    for i in range(first_weekday):
        pad_day = prev_num_days - first_weekday + 1 + i
        d = date(prev_year, prev_month, pad_day)
        days.append(CalendarDay(date=d, is_current_month=False))

    # Step 3: Current month days.
    for day_num in range(1, num_days + 1):
        d = date(year, month, day_num)

        # Compute tithi name for this day.
        tithi_name = _get_tithi_name(d, lat, lon)

        # Fetch festivals.
        from app.calc.festivals import get_festivals_for_date
        festivals = get_festivals_for_date(d, lat, lon)
        festival_names = [f.name for f in festivals]
        festival_emojis = [f.emoji for f in festivals]

        days.append(
            CalendarDay(
                date=d,
                tithi_name=tithi_name,
                festivals=festival_names,
                festival_emojis=festival_emojis,
                is_today=(d == today),
                is_current_month=True,
            )
        )

    # Step 4: Trailing filler days from next month.
    total_cells = len(days)
    trailing_count = 7 - (total_cells % 7)
    if trailing_count < 7:
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        for i in range(1, trailing_count + 1):
            d = date(next_year, next_month, i)
            days.append(CalendarDay(date=d, is_current_month=False))

    # Step 5: For a clean calendar fill, ensure total cells = multiple of 7.
    while len(days) % 7 != 0:
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        next_day = len(days) - total_cells + 1
        d = date(next_year, next_month, next_day)
        days.append(CalendarDay(date=d, is_current_month=False))

    return MonthViewData(
        year=year,
        month=month,
        month_name=month_names[month],
        days=days,
    )


def _get_tithi_name(
    d: date,
    lat: float,
    lon: float,
) -> str:
    """
    Extract the tithi name for a given date, returning empty string on failure.

    This is a helper so the month view can display tithi names succinctly
    without pulling in the full panchang machinery at every call site.
    """
    from app.calc.panchanga import get_tithi

    tithi = get_tithi(d, lat, lon)
    if tithi and tithi.name:
        paksha_initial = tithi.paksha[0] if tithi.paksha else "?"
        return f"{paksha_initial} {tithi.name}"
    return ""
