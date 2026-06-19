# Improvement — Phase 1

## Goals

1. **Location toggle** — switch between Kolkata and Bangalore via UI dropdown
2. **Calendar grid cleanup** — fix truncated names, reduce visual clutter
3. **Muhurta compaction** — dense layout that fits all 7 windows without scroll
4. **Single-page view** — today page fits in one viewport at 900px height

---

## 1. Location Toggle

### Files changed

| File | Change |
|---|---|
| `app/config.py` | Add `LOCATIONS` dict with kolkata + bangalore. Add `get_location(key)` helper. |
| `app/routes/daily.py` | Accept `loc: str = Query("kolkata")`. Resolve via `get_location()`. Pass lat/lon to `build_daily_view()`. Add `current_loc_key`, `current_loc_name`, `available_locations` to template context. |
| `app/routes/calendar.py` | Same pattern — accept `loc`, pass coords, add location context. |
| `templates/base.html` | Add `<select class="loc-picker">` dropdown in header. All HTMX links carry `?loc=` param. Footer uses `current_loc_name` instead of hardcoded "Kolkata". |
| `templates/calendar.html` | Nav links carry `&loc=` param. |
| `templates/today.html` | Nav links carry `&loc=` param. |

### Location data

```python
LOCATIONS = {
    "kolkata":  Location("Kolkata",   22.5726, 88.3639, ZoneInfo("Asia/Kolkata")),
    "bangalore": Location("Bangalore", 12.9716, 77.5946, ZoneInfo("Asia/Kolkata")),
}
```

Both use IST — only coordinates differ.

### Location propagation

- Dropdown `onchange` does full page reload with `?loc=X` appended to current URL
- All `hx-get` links include `?loc={{ current_loc_key }}` or `&loc={{ current_loc_key }}`
- Calendar prev/next/today links carry `&loc=` the same way

---

## 2. Calendar Grid Cleanup

### Problems

| Problem | Cause |
|---|---|
| Tithi name overflow | "Shukla Prathama" / "Krishna Ashtami" is ~15 chars at 0.56rem in a 80px cell |
| Text wrapping makes grid look messy | `word-break` / `overflow` not handled |
| Festival names spill out | Full festival name like "Makar Sankranti" in tiny font |
| Cells feel cramped | `min-height: 5rem`, padding `0.25rem` |

### Fixes

**`app/views/monthly.py`:**
- Change `_get_tithi_name` from `"Shukla Prathama"` → `"S Prathama"` (paksha initial + full name)

**`templates/calendar.html`:**
- Festival display: show emoji + abbreviated name, full name on hover via `title`

**`static/style.css`:**
- `calendar-day`: `min-height: 5rem` → `6rem`, padding `0.25rem` → `0.35rem 0.4rem`
- `day-number`: `font-size: 0.875rem` → `1rem`
- `day-tithi`: slightly larger font, proper text overflow handling
- `day-festival`: compact badge style

---

## 3. Muhurta Compaction

### Problems

Each muhurta card takes ~5rem vertical:
- `padding: 0.75rem 1rem` × 2 = 1.5rem
- header row: ~1.2rem
- times row: ~1rem
- description: ~1rem
- gaps: ~0.3rem

7 muhurtas × 5rem = 35rem just for the muhurta section.

### Fix: Table layout

Replace card grid with a bordered table (2px row borders):

| Name | Time Range | Badge |
|---|---|---|
| Brahma Muhurta | 03:54 — 04:42 | auspicious |
| Abhijit Muhurta | 11:30 — 12:18 | auspicious |
| Morning Sandhya | 05:30 — 05:54 | auspicious |
| Evening Sandhya | 17:06 — 17:30 | auspicious |
| Rahu Kaal | 07:30 — 08:30 | inauspicious |
| Yamaganda | 10:30 — 11:30 | inauspicious |
| Gulika Kaal | 12:30 — 13:30 | inauspicious |

Row height: ~1.8rem. Total: 7 × 1.8 = 12.6rem (saves ~22rem).

**`templates/today.html`:**
- Replace `muhurta-grid` div with a `<table class="muhurta-table">`
- Columns: Name | Time range | Badge
- Descriptions removed from visible display; use `title` attribute on row

**`static/style.css`:**
- Remove `.muhurta-grid`, `.muhurta-card`, `.muhurta-header`, `.muhurta-times`, `.muhurta-desc`
- Add `.muhurta-table` styles (compact row height, category border color)

---

## 4. Single-Page Spacing Reduction

### Target: today view at 900px viewport

| Section | Height |
|---|---|
| Header (sticky) | 55px |
| Date header + nav | 60px |
| Tithi banner | 90px |
| Sun times | 40px |
| Timeline section | 100px |
| Section title | 5px |
| Muhurta table | ~140px (7 rows) |
| Section title | 5px |
| Panchang table | ~120px (4 rows) |
| Footer | 50px |
| **Total** | **~665px** ✓ fits in 900px |

### Spacing changes (`static/style.css`)

| Selector | Property | Before | After |
|---|---|---|---|
| `.date-header` | margin-top | 1.5rem | 0.6rem |
| `.tithi-banner` | padding | 2rem 1rem 1.5rem | 1rem 0.75rem 0.75rem |
| `.tithi-banner` | margin | 0.5rem 0 1.5rem | 0.25rem 0 0.75rem |
| `.tithi-name` | font-size | 2.25rem | 1.5rem |
| `.sun-times` | margin-bottom | 1.5rem | 0.5rem |
| `.timeline-section` | margin-bottom | 2rem | 0.75rem |
| `.section-title` | margin-bottom | 0.75rem | 0.3rem |
| `.section-title` | font-size | 1.25rem | 1rem |
| `.muhurta-section` | margin-bottom | 2rem | 0.5rem |
| `.panchang-section` | margin-bottom | 2rem | 0.5rem |
| `.panchang-row` | padding | 0.6rem 1rem | 0.35rem 0.75rem |
| `.festival-section` | margin-bottom | 2rem | 0.5rem |
| `.festival-card` | padding | 0.75rem 1rem | 0.4rem 0.75rem |
| `.site-footer` | padding | 1.5rem 0 | 0.75rem 0 |

---

## 5. Festival Emojis

Each festival gets a unique emoji based on type. Displayed as small icon before the name.

**`app/models.py`:**
- Add `emoji: str = "🪷"` to `FestivalInfo`

**`app/calc/festivals.py`:**
- Set emoji per festival:
  - Makar Sankranti → ☀️
  - Pongal → 🌾
  - Republic Day → 🇮🇳
  - Independence Day → 🇮🇳
  - Gandhi Jayanti → 🕊️

**`templates/today.html` + `calendar.html`:**
- Show `{{ f.emoji }}` before festival name

---

## Decisions (Locked)

1. **Tithi abbreviation**: `"S Prathama"` (paksha initial + full name)
2. **Muhurta descriptions**: hidden from view, shown via `title` attribute on hover
3. **Festival markers**: emoji per festival type + name text
