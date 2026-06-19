"""
Daily view: assembles panchang + muhurtas + festivals into a DailyViewData model.

This is the orchestration layer that composes results from independent
calc modules.  Each data source is fetched independently so a failure
in one does not silently kill the others.
"""

import logging
from datetime import date

from app.config import DEFAULT_LOCATION
from app.models import DailyViewData
from app.calc.panchanga import compute_panchanga_day
from app.calc.muhurta import compute_all_muhurtas
from app.calc.festivals import get_festivals_for_date
from app.calc.times import compute_sunrise_sunset

logger = logging.getLogger(__name__)


def build_daily_view(
    d: date,
    lat: float = DEFAULT_LOCATION.latitude,
    lon: float = DEFAULT_LOCATION.longitude,
) -> DailyViewData:
    """
    Assemble all data needed to render a single day's page.

    Steps:
      1. Compute panchanga (tithi, nakshatra, yoga, karana).
      2. Compute sunrise/sunset for muhurta base times.
      3. Compute all muhurta windows.
      4. Look up festivals for this date.

    Each step is independent — if panchanga data is None (ephemeris missing),
    muhurtas and festivals can still be computed with fallback values.
    """
    tz = DEFAULT_LOCATION.timezone

    # Step 1: Panchanga.
    panchanga = compute_panchanga_day(d, lat, lon)

    # Step 2: Muhurtas need sunrise/sunset. Fall back from panchanga
    # or compute fresh.
    sunrise = panchanga.sunrise
    sunset = panchanga.sunset
    if sunrise is None or sunset is None:
        sunrise, sunset = compute_sunrise_sunset(d, lat, lon)

    # Step 3: Muhurta windows.
    muhurtas = compute_all_muhurtas(d, sunrise, sunset, tz)

    # Step 4: Festivals.
    festivals = get_festivals_for_date(d, lat, lon)

    return DailyViewData(
        panchanga=panchanga,
        muhurtas=muhurtas,
        festivals=festivals,
    )
