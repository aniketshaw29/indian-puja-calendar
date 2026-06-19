"""
Auspicious and inauspicious time window calculations.

Each muhurta type is computed by exactly one standalone function.
The vendored drik-panchanga library provides rahu_kalam, yamaganda_kalam,
gulika_kalam, and abhijit_muhurta directly. Other windows (Brahma Muhurta,
Sandhya) are computed from sunrise/sunset per traditional rules.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Optional

from app.config import DEFAULT_LOCATION
from app.models import MuhurtaWindow
from app.calc.engine import ephemeris_ready, Place, Date, gregorian_to_jd

logger = logging.getLogger(__name__)


def _to_datetime(decimal_hours: float, base_date: date, tz) -> datetime:
    """
    Convert decimal hours (e.g. 6.5 = 06:30) to a timezone-aware datetime.
    Handles values > 24 (next day).
    """
    day_offset = int(decimal_hours // 24)
    hour = decimal_hours % 24
    h = int(hour)
    m = int((hour - h) * 60)
    s = int(((hour - h) * 60 - m) * 60)
    day = base_date + timedelta(days=day_offset)
    return datetime(day.year, day.month, day.day, h, m, s, tzinfo=tz)


def _dms_to_datetime(dms: list, base_date: date, tz) -> datetime:
    """Convert [h, m, s] list to a timezone-aware datetime."""
    h, m_int, s = dms
    day_offset = int(h // 24)
    hour = h % 24
    day = base_date + timedelta(days=day_offset)
    return datetime(day.year, day.month, day.day, int(hour), m_int, s, tzinfo=tz)


# ---------- Individual Muhurta Functions ----------

def compute_brahma_muhurta(
    sunrise: datetime,
    tz,
) -> Optional[MuhurtaWindow]:
    """
    Brahma Muhurta: 1h36m before sunrise, lasting 48 minutes.
    Traditional rule: best time for meditation, study, and morning puja.
    """
    if not sunrise:
        return None

    start = sunrise - timedelta(hours=1, minutes=36)
    end = start + timedelta(minutes=48)

    return MuhurtaWindow(
        name="Brahma Muhurta",
        category="auspicious",
        starts_at=start,
        ends_at=end,
        description="Best time for meditation and morning puja. "
                    "Starts 1h36m before sunrise, lasts 48 minutes.",
    )


def compute_abhijit_muhurta(
    d: date, sunrise: datetime, sunset: datetime, tz,
) -> Optional[MuhurtaWindow]:
    """
    Abhijit Muhurta: 8th of 15 muhurtas during daytime.
    Considered universally auspicious regardless of other factors.
    Delegates to the vendored drik-panchanga library.
    """
    if not sunrise or not sunset:
        return None

    if ephemeris_ready():
        try:
            from app.calc.vendored_panchanga import abhijit_muhurta as _abhijit
            loc = DEFAULT_LOCATION
            tz_hours = loc.timezone.utcoffset(datetime.now()).total_seconds() / 3600
            place = Place(loc.latitude, loc.longitude, tz_hours)
            jd = gregorian_to_jd(Date(d.year, d.month, d.day))
            result = _abhijit(jd, place)
            # Returns [start_decimal, end_decimal] in local hours.
            start_dt = _to_datetime(result[0], d, tz)
            end_dt = _to_datetime(result[1], d, tz)
            return MuhurtaWindow(
                name="Abhijit Muhurta",
                category="auspicious",
                starts_at=start_dt,
                ends_at=end_dt,
                description="The midday muhurta, universally auspicious for any undertaking.",
            )
        except Exception:
            logger.exception("Failed to compute Abhijit Muhurta")

    # Fallback: approximate (local noon ± 24 min).
    day_len = (sunset - sunrise).total_seconds()
    muhurta_sec = day_len / 15.0
    start = sunrise + timedelta(seconds=muhurta_sec * 7)
    end = start + timedelta(seconds=muhurta_sec)
    return MuhurtaWindow(
        name="Abhijit Muhurta",
        category="auspicious",
        starts_at=start,
        ends_at=end,
        description="The midday muhurta, universally auspicious.",
    )


def compute_rahu_kaal(
    d: date, sunrise: datetime, sunset: datetime, tz,
) -> Optional[MuhurtaWindow]:
    """Rahu Kaal: inauspicious period. Uses vendored library if available."""
    if ephemeris_ready():
        try:
            from app.calc.vendored_panchanga import rahu_kalam as _rahu
            loc = DEFAULT_LOCATION
            tz_hours = loc.timezone.utcoffset(datetime.now()).total_seconds() / 3600
            place = Place(loc.latitude, loc.longitude, tz_hours)
            jd = gregorian_to_jd(Date(d.year, d.month, d.day))
            result = _rahu(jd, place)
            # Returns [[h1,m1,s1], [h2,m2,s2]]
            start_dt = _dms_to_datetime(result[0], d, tz)
            end_dt = _dms_to_datetime(result[1], d, tz)
            return MuhurtaWindow(
                name="Rahu Kaal",
                category="inauspicious",
                starts_at=start_dt,
                ends_at=end_dt,
                description="Inauspicious period ruled by Rahu. Avoid starting new ventures.",
            )
        except Exception:
            logger.exception("Failed to compute Rahu Kaal")

    if not sunrise or not sunset:
        return None
    weekday = d.weekday()
    slot_map = {0: 1, 1: 6, 2: 4, 3: 5, 4: 3, 5: 2, 6: 7}
    slot_index = slot_map.get(weekday, 0)
    day_sec = (sunset - sunrise).total_seconds()
    eighth = day_sec / 8.0
    start = sunrise + timedelta(seconds=eighth * slot_index)
    end = start + timedelta(seconds=eighth)
    return MuhurtaWindow(
        name="Rahu Kaal", category="inauspicious",
        starts_at=start, ends_at=end,
        description="Inauspicious period ruled by Rahu.",
    )


def compute_yamaganda(
    d: date, sunrise: datetime, sunset: datetime, tz,
) -> Optional[MuhurtaWindow]:
    """Yamaganda: inauspicious period."""
    if ephemeris_ready():
        try:
            from app.calc.vendored_panchanga import yamaganda_kalam as _yamaganda
            loc = DEFAULT_LOCATION
            tz_hours = loc.timezone.utcoffset(datetime.now()).total_seconds() / 3600
            place = Place(loc.latitude, loc.longitude, tz_hours)
            jd = gregorian_to_jd(Date(d.year, d.month, d.day))
            result = _yamaganda(jd, place)
            start_dt = _dms_to_datetime(result[0], d, tz)
            end_dt = _dms_to_datetime(result[1], d, tz)
            return MuhurtaWindow(
                name="Yamaganda", category="inauspicious",
                starts_at=start_dt, ends_at=end_dt,
                description="Inauspicious period. Avoid important activities.",
            )
        except Exception:
            logger.exception("Failed to compute Yamaganda")

    if not sunrise or not sunset:
        return None
    weekday = d.weekday()
    slot_map = {0: 6, 1: 7, 2: 0, 3: 1, 4: 2, 5: 3, 6: 4}
    slot_index = slot_map.get(weekday, 0)
    day_sec = (sunset - sunrise).total_seconds()
    eighth = day_sec / 8.0
    start = sunrise + timedelta(seconds=eighth * slot_index)
    end = start + timedelta(seconds=eighth)
    return MuhurtaWindow(
        name="Yamaganda", category="inauspicious",
        starts_at=start, ends_at=end,
        description="Inauspicious period.",
    )


def compute_gulika_kaal(
    d: date, sunrise: datetime, sunset: datetime, tz,
) -> Optional[MuhurtaWindow]:
    """Gulika Kaal: inauspicious period ruled by Gulika (son of Saturn)."""
    if ephemeris_ready():
        try:
            from app.calc.vendored_panchanga import gulika_kalam as _gulika
            loc = DEFAULT_LOCATION
            tz_hours = loc.timezone.utcoffset(datetime.now()).total_seconds() / 3600
            place = Place(loc.latitude, loc.longitude, tz_hours)
            jd = gregorian_to_jd(Date(d.year, d.month, d.day))
            result = _gulika(jd, place)
            start_dt = _dms_to_datetime(result[0], d, tz)
            end_dt = _dms_to_datetime(result[1], d, tz)
            return MuhurtaWindow(
                name="Gulika Kaal", category="inauspicious",
                starts_at=start_dt, ends_at=end_dt,
                description="Inauspicious period ruled by Gulika (son of Saturn).",
            )
        except Exception:
            logger.exception("Failed to compute Gulika Kaal")

    if not sunrise or not sunset:
        return None
    weekday = d.weekday()
    slot_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}
    slot_index = slot_map.get(weekday, 0)
    day_sec = (sunset - sunrise).total_seconds()
    eighth = day_sec / 8.0
    start = sunrise + timedelta(seconds=eighth * slot_index)
    end = start + timedelta(seconds=eighth)
    return MuhurtaWindow(
        name="Gulika Kaal", category="inauspicious",
        starts_at=start, ends_at=end,
        description="Inauspicious period ruled by Gulika.",
    )


def compute_sandhya_times(
    sunrise: datetime, sunset: datetime, tz,
) -> list[MuhurtaWindow]:
    """Sandhya (twilight) periods: ~24 min after sunrise, ~24 min before sunset."""
    if not sunrise or not sunset:
        return []
    return [
        MuhurtaWindow(
            name="Morning Sandhya", category="auspicious",
            starts_at=sunrise, ends_at=sunrise + timedelta(minutes=24),
            description="Morning twilight — favourable for prayer.",
        ),
        MuhurtaWindow(
            name="Evening Sandhya", category="auspicious",
            starts_at=sunset - timedelta(minutes=24), ends_at=sunset,
            description="Evening twilight — favourable for evening prayers.",
        ),
    ]


# ---------- Orchestration ----------

def compute_all_muhurtas(
    d: date,
    sunrise: datetime,
    sunset: datetime,
    tz,
) -> list[MuhurtaWindow]:
    """
    Compute ALL muhurta windows for a given day.
    Returns list sorted by start time.
    """
    if not sunrise or not sunset:
        return []

    muhurtas: list[MuhurtaWindow] = []

    brahma = compute_brahma_muhurta(sunrise, tz)
    if brahma:
        muhurtas.append(brahma)

    abhijit = compute_abhijit_muhurta(d, sunrise, sunset, tz)
    if abhijit:
        muhurtas.append(abhijit)

    muhurtas.extend(compute_sandhya_times(sunrise, sunset, tz))

    rahu = compute_rahu_kaal(d, sunrise, sunset, tz)
    if rahu:
        muhurtas.append(rahu)

    yama = compute_yamaganda(d, sunrise, sunset, tz)
    if yama:
        muhurtas.append(yama)

    gulika = compute_gulika_kaal(d, sunrise, sunset, tz)
    if gulika:
        muhurtas.append(gulika)

    muhurtas.sort(key=lambda m: m.starts_at)
    return muhurtas
