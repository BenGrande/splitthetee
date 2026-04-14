# Task 004: Done Report — Scoring Zones + Ruler (Phase 2)

## Status: COMPLETE

## What Was Implemented

### 1. Full Scoring Zone Computation (`api/app/services/render/scoring.py`)
- Replaced placeholder stub with full implementation
- `compute_scoring_zones(hole_layout, available_top, available_bottom, zone_ratios)` — per-hole zones
  - Above green: +5 (25%), +4 (20%), +3 (17%), +2 (15%), +1 (13%), 0 (10%) — narrowing toward green
  - Green zone: -1 (beer visible through bare glass)
  - Below green: +1 and +2 zones split remaining space
  - Configurable zone_ratios parameter
  - Automatic green detection from features with fallback
- `compute_all_scoring_zones(layout, zone_ratios)` — computes zones for all holes
  - Determines available vertical space per hole from neighboring holes
  - Uses canvas boundaries for first/last holes
- `_find_green_bounds(hole_layout)` — extracts green top/bottom y-coordinates

### 2. Scoring Zone Schema (`api/app/schemas/scoring.py`)
- `ScoringZone` — score, y_top, y_bottom, label, position ("above"/"green"/"below")
- `ScoringZoneResult` — hole_ref, zones list, green_y_top, green_y_bottom

### 3. Ruler Rendering (`api/app/services/render/svg.py`)
- `_render_ruler(zones_by_hole, draw_area, opts, font_family)` — vertical ruler on right edge
  - Vertical ruler line along right edge
  - Tick marks (8px horizontal lines) at each zone boundary
  - Score labels (right-aligned text next to ticks)
  - Hole number labels (H1, H2...) centered in each hole's vertical section
  - White color only (vinyl cutting compatible)
  - Configurable ruler_width (default 40px)
  - Added "ruler" to ALL_LAYERS, toggleable via hidden_layers

### 4. Scoring Arc Rendering
- `_render_scoring_arcs(hole, zone_result, opts)` — concentric arcs around greens
  - White outline circles expanding outward from green centroid
  - One arc per above-green zone boundary
  - Added "scoring_arcs" to ALL_LAYERS, toggleable

### 5. Hole Stats Display
- `_render_hole_stats(hole, opts, font_family)` — par/yardage/handicap labels
  - Format: "Par 4 · 385 yd · HCP 7"
  - Positioned on opposite side of hole number (avoids overlap)
  - White text, small font (3.5px), subtle opacity
  - Added "hole_stats" to ALL_LAYERS, toggleable

### 6. Scoring Preview Mode
- `_render_scoring_preview(holes, zones_by_hole, draw_area, font_family)` — colored zone bands
  - Color coding: -1=dark green, 0=light green, 1=yellow, 2=orange, 3=red-orange, 4=red, 5=dark red
  - Semi-transparent colored rectangles spanning canvas width
  - Zone labels centered in each band
  - Triggered by `mode: "scoring-preview"` in render options
  - Rendered behind features so course layout remains visible

### 7. Pipeline Integration
- `POST /api/v1/render` updated:
  - Computes scoring zones after layout, includes in response as `zones` key
  - Passes zones to SVG renderer for ruler/arcs rendering
  - Supports `mode: "scoring-preview"` for colored zone visualization
  - Custom `zone_ratios` accepted in options

### 8. Unit Tests (151 total, all passing)
- `test_scoring.py` — 14 tests (green bounds, zone computation, narrowing widths, custom ratios, multi-hole, schemas)
- `test_svg_renderer.py` — 24 tests (added 7 new: hole_stats layer, ruler with zones, ruler hidden, scoring arcs, scoring preview)
- `test_render_endpoint.py` — 8 tests (added 3 new: zones in response, scoring-preview mode)
- All 105 existing tests from Tasks 001-003 still passing

## Deviations from Spec
- None. All features implemented as specified.

## How to Test
```bash
# Run all tests
cd api && .venv/bin/python -m pytest tests/ -v

# Test scoring preview mode
# POST /api/v1/render with { "holes": [...], "options": { "mode": "scoring-preview" } }

# Toggle layers
# POST /api/v1/render with { "options": { "hidden_layers": ["ruler", "scoring_arcs"] } }
```
