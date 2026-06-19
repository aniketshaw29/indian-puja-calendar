"""
Festival date calculation.

Festivals are determined by tithi-based rules (e.g. "Shukla Paksha Dashami
in Ashvina month" = Dussehra) or solar events (e.g. Makar Sankranti).

This module currently uses a simple rule system.
Festival rules are defined in data/festivals.json for easy editing.
"""

import json
import logging
import os
from datetime import date, datetime, timedelta
from typing import Optional

from app.config import DEFAULT_LOCATION
from app.models import FestivalInfo

logger = logging.getLogger(__name__)


def _load_rules() -> list[dict]:
    """
    Load festival rules from data/festivals.json.

    Returns an empty list if the file does not exist or is malformed.
    """
    # Use the data/ directory next to this module.
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    rules_path = os.path.abspath(os.path.join(base_dir, "festivals.json"))

    if not os.path.exists(rules_path):
        logger.info("No festivals.json found at %s — festival lookup disabled", rules_path)
        return []

    try:
        with open(rules_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load festival rules: %s", exc)
        return []


# ---------- Tithi-based festival lookup ----------

def get_festivals_for_date(
    d: date,
    lat: float = DEFAULT_LOCATION.latitude,
    lon: float = DEFAULT_LOCATION.longitude,
) -> list[FestivalInfo]:
    """
    Find any festivals falling on the given date.

    This uses tithi computation to match against festival rules.
    For now returns a set of well-known approximate dates as a starting point.

    TODO: Implement full tithi-based rule matching once drik-panchanga
          lunar month detection is wired in.
    """
    festivals: list[FestivalInfo] = []

    # Seed with a few fixed solar festivals to demonstrate the pattern.
    # Makar Sankranti — Sun enters Capricorn (~Jan 14).
    if d.month == 1 and 14 <= d.day <= 16:
        festivals.append(
            FestivalInfo(
                name="Makar Sankranti",
                date=d,
                category="major",
                emoji="☀️",
                description="Sun enters Capricorn — harvest festival across India.",
            )
        )

    # Pongal / Uttarayan — same period.
    if d.month == 1 and d.day == 15:
        festivals.append(
            FestivalInfo(
                name="Pongal",
                date=d,
                category="major",
                emoji="🌾",
                description="Tamil harvest festival, first day of Uttarayana.",
            )
        )

    # Republic Day (fixed civil date).
    if d.month == 1 and d.day == 26:
        festivals.append(
            FestivalInfo(
                name="Republic Day",
                date=d,
                category="minor",
                emoji="🇮🇳",
                description="Constitution of India came into effect (1950).",
            )
        )

    # Independence Day (fixed civil date).
    if d.month == 8 and d.day == 15:
        festivals.append(
            FestivalInfo(
                name="Independence Day",
                date=d,
                category="minor",
                emoji="🇮🇳",
                description="India gained independence in 1947.",
            )
        )

    # Gandhi Jayanti (fixed civil date).
    if d.month == 10 and d.day == 2:
        festivals.append(
            FestivalInfo(
                name="Gandhi Jayanti",
                date=d,
                category="minor",
                emoji="🕊️",
                description="Birth anniversary of Mahatma Gandhi.",
            )
        )

    return festivals


def get_festivals_for_month(
    year: int,
    month: int,
    lat: float = DEFAULT_LOCATION.latitude,
    lon: float = DEFAULT_LOCATION.longitude,
) -> list[FestivalInfo]:
    """
    Get all festivals in a given Gregorian month.

    Iterates through each day of the month and checks for festivals.
    """
    import calendar

    festivals: list[FestivalInfo] = []
    _, last_day = calendar.monthrange(year, month)

    for day in range(1, last_day + 1):
        d = date(year, month, day)
        festivals.extend(get_festivals_for_date(d, lat, lon))

    return festivals
