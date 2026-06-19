# Indian Puja Calendar

Daily panchang, muhurta timings, and festival calendar for Hindu puja timelines.

Built with FastAPI + HTMX + drik-panchanga. Default location: Kolkata.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8765
```

Open http://localhost:8765

## Structure

- `app/calc/` — astronomical calculation layer (drik-panchanga)
- `app/views/` — view model assembly
- `app/routes/` — HTTP endpoints
- `app/config.py` — location and constants

## Swiss Ephemeris

For accurate panchang, download data files to `data/ephe/` from the [ephe repository](https://github.com/aloistr/swisseph/tree/master/ephe). The app works without it using time-based fallbacks.
