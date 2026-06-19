"""
Engine initialization for the vendored drik-panchanga library.

Sets up the Place namedtuple and SE_EPHE_PATH for swisseph.
"""

import logging
import os
from typing import Optional

from app.calc.vendored_panchanga import Place, Date, gregorian_to_jd

logger = logging.getLogger(__name__)

# Re-export for convenience.
from app.calc.vendored_panchanga import Place, Date, gregorian_to_jd

_ready: bool = False


def init_ephemeris(ephe_path: Optional[str] = None) -> None:
    """
    Prepare Swiss Ephemeris by setting the data file path.

    The vendored panchanga library reads SE_EPHE_PATH from the environment.
    This function sets it if a path is provided and runs a quick test.
    """
    global _ready

    if ephe_path:
        os.environ["SE_EPHE_PATH"] = ephe_path
        logger.info("Swiss Ephemeris path set to: %s", ephe_path)

    try:
        import swisseph as swe
        jd = swe.julday(2026, 6, 18, 0.0)
        _ = swe.calc_ut(jd, swe.SUN, flags=swe.FLG_SWIEPH)
        _ready = True
        logger.info("Ephemeris test OK")
    except Exception as exc:
        _ready = False
        logger.warning("Ephemeris test failed (calculations will use fallbacks): %s", exc)


def ephemeris_ready() -> bool:
    """Return True after a successful ephemeris initialization."""
    return _ready
