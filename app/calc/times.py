"""
Time utility functions used across multiple calculation modules.

Includes sunrise/sunset computation (via drik-panchanga or fallback),
day fraction helpers, and Sanskrit weekday names.
"""

from datetime import date, datetime, timedelta
from typing import Optional

from app.config import DEFAULT_LOCATION
from app.calc.engine import ephemeris_ready

# Weekday names in Sanskrit.
VAARA_NAMES = [
    "Ravivaara", "Somavaara", "Mangalavaara", "Budhavaara",
    "Guruvaara", "Shukravaara", "Shanivaara",
]


def get_vaara_name(d: date) -> str:
    """Return Sanskrit weekday name for a given date."""
    sunday_based = (d.weekday() + 1) % 7
    return VAARA_NAMES[sunday_based]


def compute_sunrise_sunset(
    d: date,
    lat: float = DEFAULT_LOCATION.latitude,
    lon: float = DEFAULT_LOCATION.longitude,
) -> tuple[Optional[datetime], Optional[datetime]]:
    """
    Compute sunrise and sunset using drik-panchanga or fallback.

    Fallback: 05:30 / 17:30 local time (approximate for most Indian cities).
    """
    tz = DEFAULT_LOCATION.timezone

    if not ephemeris_ready():
        # Approximate fallback.
        sunrise = datetime(d.year, d.month, d.day, 5, 30, 0, tzinfo=tz)
        sunset = datetime(d.year, d.month, d.day, 17, 30, 0, tzinfo=tz)
        return sunrise, sunset

    try:
        from app.calc.vendored_panchanga import (
            Place, Date, gregorian_to_jd, sunrise as _sunrise, sunset as _sunset,
        )
        tz_hours = tz.utcoffset(datetime.now()).total_seconds() / 3600
        place = Place(lat, lon, tz_hours)
        jd = gregorian_to_jd(Date(d.year, d.month, d.day))

        sr = _sunrise(jd, place)
        ss = _sunset(jd, place)

        # sr = [jd_num, [h, m, s]] — local time in dms.
        def _dms_to_dt(dms_list) -> datetime:
            h, m, s = dms_list
            day_offset = int(h // 24)
            hour = h % 24
            day = d + timedelta(days=day_offset)
            from datetime import timezone, timedelta as tdelta
            tz_aware = timezone(tdelta(hours=tz_hours))
            return datetime(day.year, day.month, day.day, int(hour), int(m), int(s), tzinfo=tz_aware)

        return _dms_to_dt(sr[1]), _dms_to_dt(ss[1])

    except Exception:
        logger = __import__("logging").getLogger(__name__)
        logger.exception("Failed to compute sunrise/sunset")
        return None, None


def compute_day_duration_minutes(sunrise: datetime, sunset: datetime) -> float:
    """Return daylight length in minutes."""
    if sunrise and sunset:
        return (sunset - sunrise).total_seconds() / 60.0
    return 0.0
