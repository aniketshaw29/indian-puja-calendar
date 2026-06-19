# Improvement — Phase 2

## Goals

1. **Add Bihari and Bengali puja events** to the festival calendar

---

## 1. Bengali Puja Events

Major Bengali festivals to add to `app/calc/festivals.py`:

| Festival | Type | Date Rule | Emoji |
|---|---|---|---|
| **Durga Puja** (Saptami–Dashami) | major | Ashvina Shukla Saptami to Dashami | 🪔 |
| **Kali Puja / Dipavali** | major | Kartika Amavasya | 🔥 |
| **Saraswati Puja** | major | Magha Shukla Panchami | 📚 |
| **Maha Shivaratri** | major | Phalguna Krishna Chaturdashi | 🔱 |
| **Janmashtami** | major | Sravana Krishna Ashtami | 🗡️ |
| **Rathayatra** | major | Asadha Shukla Dwitiya | 🛞 |
| **Naba Barsha** (Poila Boishakh) | major | April 14/15 | 🌼 |
| **Bhai Phonta / Bhai Dooj** | minor | Kartika Shukla Dwitiya | 🪷 |
| **Vasant Panchami** | minor | Magha Shukla Panchami (same as Saraswati) | 🌻 |
| **Dolyatra / Dol Purnima** | minor | Phalguna Shukla Purnima | 🎨 |
| **Jagadhatri Puja** | minor | Kartika Shukla Navami | 🕉️ |
| **Nilkantha** (Chandra Grahan) | minor | Kartika Purnima | 🌙 |

## 2. Bihari Puja Events

| Festival | Type | Date Rule | Emoji |
|---|---|---|---|
| **Chhath Puja** | major | Kartika Shukla Shashthi | 🌅 |
| **Chhath Puja (Chaiti)** | minor | Chaitra Shukla Shashthi | 🌄 |
| **Sama-Chakeva** | minor | Kartika Shukla Paksha | 🐦 |
| **Madhushravani** | minor | Sravana month | 🪷 |
| **Vrat Katha / Jivitputrika** | minor | Ashvina Krishna Ashtami | 🧿 |
| **Teej** (Hartalika) | minor | Bhadrapada Shukla Tritiya | 💃 |
| **Nag Panchami** | minor | Sravana Shukla Panchami | 🐍 |
| **Bihar Diwas** | minor | March 22 (fixed) | 🗺️ |

---

## Implementation Notes

- Tithi-based events require wiring `get_tithi()` + `get_lunar_month()` from drik-panchanga to match rules like "Ashvina Shukla Saptami"
- Some festivals are currently approximated with fixed dates until proper tithi calculation is wired in
- Add emoji field (already exists from Phase 1) — just populate per festival entry
- Festival rules go in `app/calc/festivals.py`
- Add a `data/festivals.json` structure if rules grow large enough to warrant data-driven approach

## Mapping Category → Emoji (reference)

| Category | Emoji |
|---|---|
| major | 🪔 |
| minor | 🪷 |
| vrat | 🧿 |
| sankranti | ☀️ |
