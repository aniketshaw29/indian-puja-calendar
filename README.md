# Indian Puja Calendar

Daily panchang, muhurta timings, and festival calendar for Hindu puja timelines.

Built with **FastAPI + HTMX + drik-panchanga** (Swiss Ephemeris).
Default location: **Kolkata** (22.5726°N, 88.3639°E).

## Quick Start

```powershell
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
.venv\Scripts\Activate.ps1

# 3. Install dependencies
python -m pip install -r requirements.txt
#    ^^^^ use 'python -m pip' instead of bare 'pip' if you see
#         "No Python at 'c:\python38\python.exe'" — the venv's pip
#         resolves correctly via python -m.

# 4. Start the dev server
python -m uvicorn app.main:app --reload --port 8765
```

Open **http://localhost:8765** in your browser.

## With Swiss Ephemeris (for accurate panchang)

Download ephemeris data files into `data/ephe/`:

```powershell
# https://github.com/aloistr/swisseph/tree/master/ephe
# Then set the env var before starting:
$env:SE_EPHE_PATH = "data\ephe"
python -m uvicorn app.main:app --reload --port 8765
```

Without ephemeris data, the app uses approximate times (sunrise 05:30, sunset 17:30).

## Features

- **Today's Panchang** — tithi, nakshatra, yoga, karana, sunrise/sunset
- **Muhurta Timelines** — visual day-timeline showing Brahma Muhurta, Abhijit, Rahu Kaal, Yamaganda, Gulika Kaal, Sandhya periods
- **Monthly Calendar** — month grid with tithi names and festival markers
- **HTMX Navigation** — seamless page transitions without full reloads

## Project Structure

```
indian-puja-calendar/
├── app/
│   ├── calc/               # Pure calculation layer
│   │   ├── vendored_panchanga.py   # drik-panchanga (AGPL-3.0)
│   │   ├── panchanga.py            # Tithi, nakshatra, yoga, karana
│   │   ├── muhurta.py              # Auspicious/inauspicious time windows
│   │   ├── festivals.py            # Festival date rules
│   │   ├── times.py                # Sunrise/sunset with fallback
│   │   └── engine.py               # Ephemeris init
│   ├── views/               # View model assembly
│   ├── routes/              # HTTP endpoints
│   ├── models.py            # Pydantic schemas
│   ├── config.py            # Location, ayanamsa, port
│   └── main.py              # FastAPI app
├── templates/               # Jinja2 + HTMX
├── static/style.css         # Bengali Hindu design system
├── data/                    # Ephemeris data (user-downloaded)
├── AGENTS.md
└── README.md
```

## Configuration

Edit `app/config.py` to change:

| Setting | Default | Notes |
|---|---|---|
| Location | Kolkata | lat, lon, timezone |
| Ayanamsa | Lahiri | Lahiri = Chitrapaksha (standard) |
| Port | 8765 | Dev server port |
| Ephemeris path | None | Set via `SE_EPHE_PATH` env var |

## Adding Muhurtas

1. Write one pure function in `app/calc/muhurta.py` returning `MuhurtaWindow`.
2. Call it from `compute_all_muhurtas()` (same file).
3. The route and template pick it up automatically.

## Adding Festivals

Add date-based rules in `app/calc/festivals.py` or create `data/festivals.json`.

## Documentation

- **[AGENTS.md](./AGENTS.md)** — compact reference for AI coding sessions. Setup commands, architecture diagram, conventions, design tokens, and library notes. Read this before making changes.

## Dependencies

- `fastapi` — web framework
- `uvicorn` — ASGI server
- `jinja2` — templating
- `pyswisseph` — Swiss Ephemeris Python bindings
- `pytz` / `tzdata` — timezone support

## License

This project uses the vendored [drik-panchanga](https://github.com/bdsatish/drik-panchanga) library (AGPL-3.0).
