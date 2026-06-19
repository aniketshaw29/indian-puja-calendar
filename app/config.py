"""
Central configuration for the puja calendar application.

All location, timezone, and astronomical constants live here
so they can be changed in one place without touching calculation logic.
"""

from zoneinfo import ZoneInfo
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Location:
    """Geographic coordinates and timezone for panchang calculations."""
    name: str
    latitude: float
    longitude: float
    timezone: ZoneInfo


@dataclass(frozen=True)
class Ayanamsa:
    """
    Ayanamsa (precession) system for sidereal calculations.

    Lahiri (Chitrapaksha) is the standard ayanamsa used in Indian panchangas.
    """
    name: str
    value: float  # Degrees of precession offset
    # drik-panchanga uses: 0 = Lahiri, 1 = Raman, 2 = Krishnamurti, 3 = Yukteshwar
    drik_id: int = 0


# ---------- Default location: Kolkata ----------
DEFAULT_LOCATION = Location(
    name="Kolkata",
    latitude=22.5726,
    longitude=88.3639,
    timezone=ZoneInfo("Asia/Kolkata"),
)

# ---------- Ayanamsa ----------
DEFAULT_AYANAMSA = Ayanamsa(
    name="Lahiri (Chitrapaksha)",
    value=24.0,  # Approximate; drik-panchanga calculates precise value per date
    drik_id=0,
)

# ---------- Server ----------
HOST = "127.0.0.1"
PORT = 8765
DEV_MODE = True

# ---------- Swiss Ephemeris ----------
# Set to a directory path if you have downloaded sweph data files.
# If None, ephemeris data is expected in the default sweph search path.
SWEPH_PATH = None

# ---------- Season definitions for festival rules ----------
# Hindu lunar months and their Gregorian approximations
HINDU_MONTHS = [
    "Chaitra", "Vaisakha", "Jyaistha", "Asadha",
    "Sravana", "Bhadrapada", "Asvina", "Kartika",
    "Margasirsa", "Pausa", "Magha", "Phalguna",
]

# Mapping of English weekday indices to planet rulers (for Rahu Kaal etc.)
WEEKDAY_RULERS = {
    0: "Moon",    # Monday
    1: "Mars",    # Tuesday
    2: "Mercury", # Wednesday
    3: "Jupiter", # Thursday
    4: "Venus",   # Friday
    5: "Saturn",  # Saturday
    6: "Sun",     # Sunday
}
