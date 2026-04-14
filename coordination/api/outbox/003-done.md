# Task 003: Done Report — Layout Engine, SVG Renderer, Glass Template & Settings

## Status: COMPLETE

## What Was Implemented

### 1. Layout Engine (`api/app/services/render/layout.py`)
- `compute_layout(holes, opts)` — full port from `layout-engine.js` (477 lines)
  - Difficulty-based angles (35-55 deg), yardage-proportional lengths
  - Per-glass difficulty normalization
  - `_simulate_zigzag()` — zigzag positioning with direction reversal, target sweep logic
  - `_transform_hole_features()` — geo-coord to canvas projection with lat correction, rotation, corridor clamping, water feature scaling
  - `_fix_overlaps()` — shifts subsequent holes down to prevent Y overlap
  - `_pack_holes()` — removes excess vertical gaps (4px target)
  - `_enforce_slope()` — ensures tee above green (6px min drop)
  - `_rescale_to_fill()` — fills canvas after adjustments (called twice as in JS)
- `split_into_glasses(holes, glass_count)` — divides holes for 1/2/3/6 glasses

### 2. Glass Template (`api/app/services/render/glass_template.py`)
- `compute_glass_template(opts)` — truncated cone → annulus sector geometry
  - Defaults: 146mm height, 43mm/30mm radii, 3mm wall, 5mm base
  - Computes slant height, inner/outer radii, sector angle, SVG dims, volume_ml
- `glass_wrap_path(template)` — SVG path d-attribute for glass outline
- `create_warp_function(template, w, h)` — rect-to-polar coordinate mapping
- `warp_layout(layout, template, padding_opts)` — warps entire layout to glass space
- `compute_fill_height(template, volume_ml)` — binary search for liquid fill level

### 3. SVG Renderer (`api/app/services/render/svg.py`)
- `render_svg(layout, opts)` — full port from `svg-renderer.js` (206 lines)
  - Per-hole color coding with 18-hue cycle
  - HSL tinting for fairway/rough/tee/green (35% fill, 25% stroke)
  - 9-layer system with toggleable visibility
  - Feature polygon/polyline rendering
  - Hole number circles and par labels at green centroids
  - Glass/warped mode: clip path, curved text paths
  - Rect mode: rotated course name, hole range, yardages on left edge
  - Logo support (data URL image)
  - Font family customization
  - All color utility functions (hex→rgb→hsl→rgb roundtrip, tinting)

### 4. Scoring Zones (`api/app/services/render/scoring.py`)
- `compute_scoring_zones(hole, green_bbox)` — stub with working placeholder zones
  - Generates zones above green (+5 widest to 0), green zone, zones below (+1, +2)
  - Detects green position from features or bbox parameter

### 5. Render Endpoints (`api/app/api/v1/render.py`)
- `POST /api/v1/render` — computes layout + renders SVG from hole data
  - Supports rect and glass modes, glass splitting, custom styles/fonts/layers
- `POST /api/v1/render/glass-template` — computes glass template geometry + SVG path
- Registered in `api/app/api/router.py`

### 6. Settings Endpoints (`api/app/api/v1/settings.py`)
- `POST /api/v1/settings` — saves design config to MongoDB `design_settings` collection
- `GET /api/v1/settings` — lists all saved settings (newest first)
- `GET /api/v1/settings/{setting_id}` — loads specific settings document
- Proper error handling (400 for missing name, 404 for not found)

### 7. Unit Tests (134 total, all passing)
- `test_layout.py` — 13 tests (layout computation, zigzag, overlaps, slope, glass splitting)
- `test_glass_template.py` — 11 tests (geometry, paths, fill height, warp function, layout warping)
- `test_svg_renderer.py` — 17 tests (color utils, helpers, rendering in rect/warped modes)
- `test_scoring.py` — 5 tests (zone generation, green detection, edge cases)
- `test_render_endpoint.py` — 10 tests (render endpoint, glass template endpoint, settings CRUD)
- Plus 78 existing tests from Tasks 001-002 — all still passing

## Deviations from Spec
- None. All algorithms faithfully ported from the JS reference files.

## How to Test
```bash
# Run all unit tests
cd api && .venv/bin/python -m pytest tests/ -v

# Manual test (requires running server)
# POST http://localhost:8000/api/v1/render with hole data
# POST http://localhost:8000/api/v1/render/glass-template with glass dims
# POST/GET http://localhost:8000/api/v1/settings
```
