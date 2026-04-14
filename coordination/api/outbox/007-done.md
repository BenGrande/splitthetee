# Task 007: Done Report — Phase 5 API Polish & Integration

## Status: COMPLETE

## What Was Implemented

### 1. Logo Integration (`api/app/api/v1/assets.py`)
- `GET /api/v1/assets/logo` — returns logo as base64 data URL
- Reads from `public/logo.png` with multiple path resolution candidates
- Caches data URL in memory after first read
- Registered in router

### 2. QR Code Embedding in SVG
- Added `qr_svg` option to render pipeline
- `_render_embedded_qr()` in svg.py — positions QR at bottom-right
- Supports both rect and glass/warped modes
- Passed through from render endpoint options

### 3. Scoring Zone Fine-Tuning (`api/app/services/render/scoring.py`)
- `_compute_difficulty_factor(hole)` — handicap/difficulty-based zone scaling
  - Handicap 1 (hardest) → 1.15x wider zones
  - Handicap 18 (easiest) → 0.85x tighter zones
- `_compute_par_factor(hole)` — par-based adjustment
  - Par 3 → 0.90x (tighter, precision holes)
  - Par 5 → 1.10x (more forgiving, long holes)
- Combined factor applied to upper zones (+5, +4, +3) with normalization
- Zone ratios auto-adjusted per hole while maintaining proportions

### 4. Course Font Intelligence (`api/app/services/font_hints.py`)
- `get_font_hint(course_name)` — maps course names to suggested fonts
- 15 well-known courses mapped (Pebble Beach, Augusta, St Andrews, etc.)
- Case-insensitive matching with partial match support
- `font_hint` included in course-holes endpoint response

### 5. API Health & Status
- `GET /api/v1/status` — returns API version, MongoDB connection status, cache stats (search/map/bundle counts), active game sessions count
- `POST /api/v1/admin/cleanup` — manually clears expired cache entries from all three cache collections
- Request logging middleware — logs method, path, status code, duration (ms) for every request

### 6. Files Modified/Created
- CREATE: `api/app/services/font_hints.py`
- CREATE: `api/app/api/v1/assets.py`
- MODIFY: `api/app/services/render/scoring.py` (difficulty/par factors)
- MODIFY: `api/app/services/render/svg.py` (QR embedding)
- MODIFY: `api/app/api/v1/render.py` (qr_svg option)
- MODIFY: `api/app/api/v1/holes.py` (font_hint in response)
- MODIFY: `api/app/api/router.py` (assets router)
- MODIFY: `api/app/main.py` (logging middleware, status/cleanup endpoints)

### 7. Unit Tests (242 total, all passing)
- `test_polish.py` — 25 new tests covering:
  - Font hints (exact match, case insensitive, partial match, no match, empty/None)
  - Difficulty factor (hard/easy/mid/no-data)
  - Par factor (par 3/4/5/none)
  - Scoring zones with factors (hard vs easy, par 3 vs par 5)
  - Logo endpoint (found, not found)
  - Status endpoint (version)
  - QR embedding (with/without option)
  - Holes endpoint cache hit
- All 217 existing tests still passing

## Deviations from Spec
- None significant.

## How to Test
```bash
cd api && .venv/bin/python -m pytest tests/ -v

# Logo endpoint
# GET /api/v1/assets/logo

# Status endpoint
# GET /api/v1/status

# Cache cleanup
# POST /api/v1/admin/cleanup

# Font hint in course-holes response
# GET /api/v1/course-holes?lat=36.5626&lng=-121.9191
```
