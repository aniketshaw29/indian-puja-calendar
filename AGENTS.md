# AGENTS.md — Indian Puja Calendar

## Setup & Dev Commands

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
$env:SE_EPHE_PATH = "data\ephe"  # optional: sweph data
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8765
```

Swiss Ephemeris data (optional, for accurate panchang):
Download into `data/ephe/` from https://github.com/aloistr/swisseph/tree/master/ephe
Set `SE_EPHE_PATH` env var to point to that directory.

## Architecture (strict layering)

```
app/
  calc/       Pure functions, no web imports. One file per domain.
  views/      Orchestrates calc results into view models.
  routes/     Thin HTTP handlers, delegates to views.
  models.py   Pydantic schemas shared across layers.
  config.py   Location, timezone, ayanamsa, server settings.
  main.py     FastAPI app factory, lifespan (ephemeris init), route registration.
```

- `calc/muhurta.py`: each muhurta type = exactly one standalone function.
- `calc/panchanga.py`: each panchang element (tithi, nakshatra, yoga, karana) = one function.
- `calc/festivals.py`: festival rules loaded from `data/festivals.json` if present.
- `calc/times.py`: sunrise/sunset fallback (approx 05:30/17:30) if ephemeris missing.

## Vendored Library

`app/calc/vendored_panchanga.py` is the drik-panchanga library (AGPL-3.0)
from https://github.com/bdsatish/drik-panchanga. Modified only to read
`SE_EPHE_PATH` from env var instead of hardcoded Linux path.
Our calc layer wraps it for consistent error handling.

## Key Conventions

- Every calculation function returns `Optional[Model]` — failures never crash the page.
- `config.py` is the single source of truth for location/constants. Change location there.
- Templates use HTMX for navigation (`hx-get`, `hx-target`, `hx-swap`).
- CSS in `static/style.css` — palette derived from Bengali Hindu traditions (sindur, palm-leaf, gold).

## Defaults

- Location: Kolkata (22.5726°N, 88.3639°E, Asia/Kolkata)
- Ayanamsa: Lahiri (Chitrapaksha)
- Dev port: 8765

## Visual Design

- Display font: Noto Serif Bengali. Body font: Inter.
- Color system: `--color-primary: #C73B1D` (vermilion/sindur), `--color-gold: #B8862D`, `--color-bg: #FBF6EF` (palm-leaf).
- Signature element: horizontal day timeline showing muhurta blocks from sunrise→sunset, with a pulsing "now" marker.
- Reference `app/routes/daily.py:_build_timeline_context()` for timeline segment computation.

## Adding a New Muhurta

1. Write one pure function in `calc/muhurta.py` returning `MuhurtaWindow`.
2. Call it from `compute_all_muhurtas()`.
3. The route and template pick it up automatically.

## Adding a New Festival

Add a rule to `data/festivals.json` (or hardcode in `calc/festivals.py` for tithi-based rules).
