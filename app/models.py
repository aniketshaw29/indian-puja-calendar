"""
Pydantic models for all data shapes in the application.

Every function that returns structured data uses one of these types.
This keeps a clear contract between the calc, view, and route layers.
"""

from datetime import date, datetime, time
from typing import Optional
from pydantic import BaseModel


class SunTimeInfo(BaseModel):
    """Sunrise and sunset for a given date and location."""
    date: date
    sunrise: datetime
    sunset: datetime
    day_duration_minutes: float


class TithiInfo(BaseModel):
    """A lunar day (tithi) with its index, name, and time range."""
    index: int          # 1–30
    name: str           # e.g. "Prathama", "Dwitiya", ...
    paksha: str         # "Shukla" (bright) or "Krishna" (dark)
    starts_at: datetime
    ends_at: datetime
    is_auspicious: bool = True


class NakshatraInfo(BaseModel):
    """A lunar mansion (nakshatra)."""
    index: int          # 1–27
    name: str           # e.g. "Ashwini", "Bharani", ...
    starts_at: datetime
    ends_at: datetime


class YogaInfo(BaseModel):
    """A yoga (combination of sun + moon longitudes)."""
    index: int          # 1–27
    name: str
    starts_at: datetime
    ends_at: datetime


class KaranaInfo(BaseModel):
    """A karana (half of a tithi)."""
    index: int          # 1–11
    name: str
    starts_at: datetime
    ends_at: datetime


class PanchangaDay(BaseModel):
    """Complete panchang for a single day."""
    date: date
    sunrise: datetime
    sunset: datetime
    tithi: Optional[TithiInfo] = None
    nakshatra: Optional[NakshatraInfo] = None
    yoga: Optional[YogaInfo] = None
    karana: Optional[KaranaInfo] = None
    vaara: str          # Weekday name in Sanskrit / English


class MuhurtaWindow(BaseModel):
    """
    A named auspicious (or inauspicious) time window.

    Examples: Brahma Muhurta, Abhijit, Rahu Kaal.
    """
    name: str
    category: str       # "auspicious", "inauspicious", "neutral"
    starts_at: datetime
    ends_at: datetime
    description: str = ""


class FestivalInfo(BaseModel):
    """A festival or religious observance for a given date."""
    name: str
    date: date
    category: str       # "major", "minor", "vrat", "sankranti"
    description: str = ""


class DailyViewData(BaseModel):
    """All data needed to render a single day's page."""
    panchanga: PanchangaDay
    muhurtas: list[MuhurtaWindow]
    festivals: list[FestivalInfo]


class CalendarDay(BaseModel):
    """A single cell in a monthly calendar grid."""
    date: date
    tithi_name: str = ""
    festivals: list[str] = []
    is_today: bool = False
    is_current_month: bool = True


class MonthViewData(BaseModel):
    """All data needed to render a monthly calendar."""
    year: int
    month: int
    month_name: str
    days: list[CalendarDay]
