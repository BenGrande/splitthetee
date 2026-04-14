# Task 005: Done Report — Cricut 3-Color SVG Export (Phase 3)

## Status: COMPLETE

## What Was Implemented

### 1. Cricut Export Service (`api/app/services/render/cricut.py`)

#### `render_cricut_white(layout, zones_by_hole, template, opts)`
- All feature outlines (stroke only, no fills) in glass layout positions
- Scoring arc circles around greens
- Hole number circles and labels
- Hole stats (P4, 400y, H5 format)
- Ruler tick marks and score labels on right edge
- Course name text (vertical on left edge or along text arc in warped mode)
- Glass outline in warped mode
- 10mm scale verification ruler at bottom
- White stroke, 0.5px hairline width
- mm units when glass template available

#### `render_cricut_green(layout, opts)`
- Extracts all green and tee features from all holes
- Compact bin-packing arrangement for efficient vinyl cutting
- Reference labels (G1, T1, G2, etc.) on each piece
- mm units, scale ruler included

#### `render_cricut_tan(layout, opts)`
- Extracts all bunker features from all holes
- Same compact arrangement algorithm
- Reference labels (B1, B2, etc.)
- mm units, scale ruler included

#### `render_cricut_guide(layout, opts)`
- Full glass layout with color-coded outlines
- Green/tee pieces in green, bunkers in tan, other features in gray
- Reference labels on all colored pieces for manual placement
- Works in both rect and warped modes

### 2. Compact Arrangement Algorithm (`_compact_arrange`)
- Sort pieces by height descending (tall pieces first)
- Row-based bin packing: left-to-right with padding, wrap on overflow
- Each piece normalized to origin, then translated to compact position
- Configurable canvas width and padding
- Returns placed coordinates and canvas height

### 3. API Endpoint Updates (`api/app/api/v1/render.py`)
- `mode: "cricut-white"` → white vinyl layer SVG
- `mode: "cricut-green"` → green vinyl compact arrangement SVG
- `mode: "cricut-tan"` → tan vinyl compact arrangement SVG
- `mode: "cricut-all"` → all three layers + placement guide
- `POST /api/v1/render/cricut` — dedicated endpoint returning `{ white, green, tan, guide }`
- Shared `_build_layout_and_zones()` helper to avoid duplication

### 4. SVG Requirements for Cricut
- mm units in SVG width/height attributes
- No fills — stroke-only paths for cutting
- 0.5px hairline stroke width
- Clean, non-overlapping paths
- 10mm scale verification ruler on every SVG

### 5. Unit Tests (184 total, all passing)
- `test_cricut.py` — 28 tests covering:
  - Bounding box computation
  - Feature extraction by category (with hole ref preservation)
  - Compact arrangement (packing, row wrapping, empty input)
  - Scale ruler generation
  - White layer (outlines, hole numbers, stats, course name, warped mode, scale ruler)
  - Green layer (labels, mm units, scale ruler, empty features)
  - Tan layer (labels, mm units, empty bunkers)
  - Placement guide (labels, warped mode)
- `test_render_endpoint.py` — 5 new tests (cricut-white/green/tan/all modes, dedicated endpoint)
- All 151 existing tests still passing

## Deviations from Spec
- None significant. All specified features implemented.

## How to Test
```bash
cd api && .venv/bin/python -m pytest tests/ -v

# Cricut export via render endpoint
# POST /api/v1/render { "holes": [...], "options": { "mode": "cricut-white" } }
# POST /api/v1/render { "holes": [...], "options": { "mode": "cricut-all" } }

# Dedicated cricut endpoint (always warps to glass)
# POST /api/v1/render/cricut { "holes": [...], "options": {} }
```
