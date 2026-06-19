"""
Panchang calculation — one function per panchang element, backed by drik-panchanga.

Each element (tithi, nakshatra, yoga, karana) is computed independently.
If ephemeris is unavailable, functions return None and the app uses fallbacks.
"""

import logging
from datetime import date, datetime, timezone, timedelta
from typing import Optional

from app.config import DEFAULT_LOCATION
from app.models import (
    PanchangaDay,
    TithiInfo,
    NakshatraInfo,
    YogaInfo,
    KaranaInfo,
)
from app.calc.engine import ephemeris_ready, Place, Date, gregorian_to_jd
from app.calc.times import get_vaara_name

logger = logging.getLogger(__name__)

# Tithi names in Sanskrit.
TITHI_NAMES = [
    "Prathama", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Prathama", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]

# Nakshatra names in Sanskrit.
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# Yoga names in Sanskrit.
YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti",
]

# Karana names in Sanskrit (11 unique, cycle).
KARANA_NAMES = [
    "Bava", "Balava", "Kaulava", "Taitila", "Gara",
    "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga",
    "Kimstughna",
]


def _dms_to_datetime(dms: list, base_date: date, tz_offset_hours: float) -> datetime:
    """
    Convert drik-panchanga's [h, m, s] local time to a timezone-aware datetime.

    The hours can be > 24 (indicating next day). We handle that by adjusting
    the date forward.
    """
    h, m, s = dms
    day_offset = int(h // 24)
    hour = h % 24
    d = base_date
    if day_offset > 0:
        from datetime import timedelta
        d = d + timedelta(days=day_offset)

    # Build a naive datetime and attach the target timezone.
    dt = datetime(d.year, d.month, d.day, int(hour), int(m), int(s))
    # Create timezone with the given offset.
    from datetime import timezone, timedelta
    tz = timezone(timedelta(hours=tz_offset_hours))
    return dt.replace(tzinfo=tz)


def _make_place() -> Place:
    """Create a Place namedtuple from the app's default location config."""
    loc = DEFAULT_LOCATION
    # timezone in hours (e.g. +5.5 for IST)
    tz_hours = loc.timezone.utcoffset(datetime.now()).total_seconds() / 3600
    return Place(loc.latitude, loc.longitude, tz_hours)


# ---------- Tithi ----------

def get_tithi(
    d: date,
    lat: float = DEFAULT_LOCATION.latitude,
    lon: float = DEFAULT_LOCATION.longitude,
) -> Optional[TithiInfo]:
    if not ephemeris_ready():
        return None
    try:
        from app.calc.vendored_panchanga import tithi as _tithi
        place = _make_place()
        jd = gregorian_to_jd(Date(d.year, d.month, d.day))
        result = _tithi(jd, place)
        idx = result[0]  # 1-based
        end_dms = result[1]
        tz_hours = place.timezone
        end_dt = _dms_to_datetime(end_dms, d, tz_hours)
        # Start time: previous day at this tithi's start (rough sunrise).
        from datetime import timedelta
        start_dt = end_dt - timedelta(hours=24)

        name = TITHI_NAMES[(idx - 1) % 30]
        paksha = "Shukla" if 1 <= idx <= 15 else "Krishna"

        return TithiInfo(
            index=idx,
            name=name,
            paksha=paksha,
            starts_at=start_dt,
            ends_at=end_dt,
        )
    except Exception:
        logger.exception("Failed to compute tithi for %s", d)
        return None


# ---------- Nakshatra ----------

def get_nakshatra(
    d: date,
    lat: float = DEFAULT_LOCATION.latitude,
    lon: float = DEFAULT_LOCATION.longitude,
) -> Optional[NakshatraInfo]:
    if not ephemeris_ready():
        return None
    try:
        from app.calc.vendored_panchanga import nakshatra as _nakshatra
        place = _make_place()
        jd = gregorian_to_jd(Date(d.year, d.month, d.day))
        result = _nakshatra(jd, place)
        idx = result[0]
        end_dms = result[1]
        tz_hours = place.timezone
        end_dt = _dms_to_datetime(end_dms, d, tz_hours)
        from datetime import timedelta
        start_dt = end_dt - timedelta(hours=24)
        name = NAKSHATRA_NAMES[(idx - 1) % 27]
        return NakshatraInfo(
            index=idx, name=name, starts_at=start_dt, ends_at=end_dt,
        )
    except Exception:
        logger.exception("Failed to compute nakshatra for %s", d)
        return None


# ---------- Yoga ----------

def get_yoga(
    d: date,
    lat: float = DEFAULT_LOCATION.latitude,
    lon: float = DEFAULT_LOCATION.longitude,
) -> Optional[YogaInfo]:
    if not ephemeris_ready():
        return None
    try:
        from app.calc.vendored_panchanga import yoga as _yoga
        place = _make_place()
        jd = gregorian_to_jd(Date(d.year, d.month, d.day))
        result = _yoga(jd, place)
        idx = result[0]
        end_dms = result[1]
        tz_hours = place.timezone
        end_dt = _dms_to_datetime(end_dms, d, tz_hours)
        from datetime import timedelta
        start_dt = end_dt - timedelta(hours=24)
        name = YOGA_NAMES[(idx - 1) % 27]
        return YogaInfo(
            index=idx, name=name, starts_at=start_dt, ends_at=end_dt,
        )
    except Exception:
        logger.exception("Failed to compute yoga for %s", d)
        return None


# ---------- Karana ----------

def get_karana(
    d: date,
    lat: float = DEFAULT_LOCATION.latitude,
    lon: float = DEFAULT_LOCATION.longitude,
) -> Optional[KaranaInfo]:
    if not ephemeris_ready():
        return None
    try:
        from app.calc.vendored_panchanga import karana as _karana
        place = _make_place()
        jd = gregorian_to_jd(Date(d.year, d.month, d.day))
        result = _karana(jd, place)
        idx = result[0]
        end_dms = result[1]
        tz_hours = place.timezone
        end_dt = _dms_to_datetime(end_dms, d, tz_hours)
        from datetime import timedelta
        start_dt = end_dt - timedelta(hours=12)
        karana_idx = ((idx - 1) % 11)
        name = KARANA_NAMES[karana_idx]
        return KaranaInfo(
            index=idx, name=name, starts_at=start_dt, ends_at=end_dt,
        )
    except Exception:
        logger.exception("Failed to compute karana for %s", d)
        return None


# ---------- Orchestration ----------

def compute_panchanga_day(
    d: date,
    lat: float = DEFAULT_LOCATION.latitude,
    lon: float = DEFAULT_LOCATION.longitude,
) -> PanchangaDay:
    """
    Assemble the full panchanga for a single day.

    Each element computed independently — a failure in one does not block others.
    """
    from app.calc.times import compute_sunrise_sunset
    sunrise, sunset = compute_sunrise_sunset(d, lat, lon)

    return PanchangaDay(
        date=d,
        sunrise=sunrise,
        sunset=sunset,
        tithi=get_tithi(d, lat, lon),
        nakshatra=get_nakshatra(d, lat, lon),
        yoga=get_yoga(d, lat, lon),
        karana=get_karana(d, lat, lon),
        vaara=get_vaara_name(d),
    )
