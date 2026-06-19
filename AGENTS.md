# AGENTS.md — Indian Puja Calendar

> **For full project docs, see [README.md](./README.md).** This file is a compact reference for AI coding sessions — setup, architecture, conventions. It assumes you've read README.md first.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8765
# Open http://localhost:8765
```

**Swiss Ephemeris** (optional, enables accurate panchang):
Download data into `data/ephe/` from https://github.com/aloistr/swisseph/tree/master/ephe
Set env `SE_EPHE_PATH=data\ephe` before start.
Without it, sunrise=05:30/sunset=17:30 fallback is used.

> On Windows, `tzdata` pip package is required for `zoneinfo` timezone support.
> Already in requirements.txt.

## Architecture

```
app/
  calc/              Pure functions, no web imports
    vendored_panchanga.py   AGPL-3.0, from bdsatish/drik-panchanga
    panchanga.py            tithi/nakshatra/yoga/karana (each = one function)
    muhurta.py              Brahma/Abhijit/Rahu/Gulika/Yamaganda/Sandhya (each = one fn)
    festivals.py            Date-based festival rules
    times.py                Sunrise/sunset with fallback
    engine.py               Ephemeris init, Place/Date re-exports
  views/              Orchestrates calc results into view models
  routes/             Thin HTTP handlers, delegates to views
  models.py           Pydantic schemas
  config.py           Location (Kolkata), ayanamsa (Lahiri), port (8765)
  main.py             FastAPI app factory with lifespan
templates/            Jinja2 + HTMX
static/style.css      Bengali Hindu palette (sindur, palm-leaf, gold)
```

## Conventions

- Every calc function returns `Optional[Model]` — failures never crash the page.
- Adding a muhurta: write one function in `calc/muhurta.py`, wire into `compute_all_muhurtas()`.
- Adding a festival: add rule in `calc/festivals.py` (or `data/festivals.json`).
- `config.py` is single source of truth for location/constants.
- `Jinja2Templates.TemplateResponse(request, name, context)` — request **must** be first arg.
- HTMX for navigation: `hx-get`, `hx-target="main"`, `hx-swap="innerHTML"`.

## Visual Design

| Token | Value | Meaning |
|---|---|---|
| `--color-bg` | `#FBF6EF` | Palm-leaf manuscript |
| `--color-primary` | `#C73B1D` | Vermilion (sindur) |
| `--color-gold` | `#B8862D` | Temple gold |
| Display | Noto Serif Bengali | Cultural gravitas |
| Body | Inter | Clean data |
| Signature | Horizontal day timeline | Muhurta blocks sunrise→sunset, pulsing "now" marker |

## Vendored Library

`app/calc/vendored_panchanga.py` is drik-panchanga (AGPL-3.0, bdsatish/drik-panchanga).
Only change: reads `SE_EPHE_PATH` env var instead of hardcoded Linux path.
