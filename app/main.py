"""
FastAPI application entrypoint.

Startup lifecycle:
  1. Configure logging.
  2. Initialize ephemeris (drik-panchanga / Swiss Ephemeris).
  3. Mount static files and register routes.

Start with:
    uvicorn app.main:app --reload --port 8765
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import DEV_MODE, SWEPH_PATH, HOST, PORT

# ---------- Logging ----------

logging.basicConfig(
    level=logging.DEBUG if DEV_MODE else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------- Lifespan ----------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle: startup → yield → shutdown.

    Startup:
      1. Log application start.
      2. Initialize the Swiss Ephemeris engine.
      3. Log whether ephemeris is ready (or if fallbacks will be used).

    Shutdown:
      1. Clean log message.
    """
    # --- STARTUP ---
    logger.info("Puja Calendar starting on http://%s:%d", HOST, PORT)
    logger.info("Ephemeris path: %s", SWEPH_PATH or "default search path")

    from app.calc.engine import init_ephemeris, ephemeris_ready

    # Step 1: Initialize Swiss Ephemeris.
    init_ephemeris(SWEPH_PATH)

    if ephemeris_ready():
        logger.info("Ephemeris ready — full panchang calculations enabled")
    else:
        logger.warning(
            "Swiss Ephemeris data not found. "
            "Panchang calculations will use fallback values. "
            "Download ephemeris data to data/ephe/ for full accuracy."
        )

    yield

    # --- SHUTDOWN ---
    logger.info("Puja Calendar shutting down")


# ---------- App factory ----------

app = FastAPI(
    title="Indian Puja Calendar",
    description="Daily panchang, muhurtas, and festival timelines",
    version="0.1.0",
    lifespan=lifespan,
)

# Step 2: Mount static files.
import os
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(os.path.abspath(static_dir)):
    app.mount("/static", StaticFiles(directory=os.path.abspath(static_dir)), name="static")

# Step 3: Register route modules.
from app.routes.daily import router as daily_router
from app.routes.calendar import router as calendar_router

app.include_router(daily_router)
app.include_router(calendar_router)


# ---------- Direct execution ----------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=DEV_MODE)
