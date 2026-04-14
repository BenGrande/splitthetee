# Task 003: Layout Engine, SVG Renderer, Glass Template & Settings

## Priority: HIGH — needed for designer preview and export

## Prerequisites
- Task 001 (schemas) and Task 002 (OSM + holes) must be complete

## What to Build

### 1. Layout Engine (`api/app/services/render/layout.py`)

Port from `public/layout-engine.js` (~477 lines). Main function: `compute_layout(holes, opts)`

**Key algorithm steps:**

#### Angle & Length Calculation
- Difficulty-based angles: 35 deg (hardest) to 55 deg (easiest)
- Yardage-proportional lengths relative to total course yardage
- Per-glass difficulty normalization

#### Zigzag Positioning (`simulate_zigzag()`)
- Arrange holes in zigzag pattern down canvas
- Alternate direction when accumulated horizontal sweep exceeds target
- Target sweep: 70% (1-3 holes), 60% (4-6 holes), 50% (7+)
- Hole padding: 2% gap
- Normalized X range: 0.12 to 0.88

#### Feature Transformation (`transform_hole_features()`)
- Project OSM geo-coords to canvas space
- Latitude correction (cosine adjustment)
- Rotation based on hole direction
- Scaling based on yardage
- Perpendicular corridor clamping
- Water features scaled individually if oversized

#### Post-processing
- `fix_overlaps()` — shift holes down to prevent Y overlap
- `pack_holes()` — remove excess vertical gaps (4px minimum target)
- `enforce_slope()` — ensure tee above green (6px min drop)
- `rescale_to_fill()` — fill canvas after adjustments

#### Glass Grouping (`split_into_glasses()`)
- Divide holes for 1, 2, 3, or 6 glasses

**Default canvas**: 900x700px, margins 30px, text margin 60px

Port this FAITHFULLY — the layout algorithm is complex and must match the old behavior. Read `public/layout-engine.js` carefully.

### 2. Glass Template (`api/app/services/render/glass_template.py`)

Port from `public/glass-template.js` (~274 lines).

**Functions to port:**
- `compute_glass_template(opts)` — truncated cone → annulus sector geometry
  - Inputs: glass_height (146mm), top_radius (43mm), bottom_radius (30mm), wall_thickness (3mm), base_thickness (5mm)
  - Outputs: slant_height, inner_r, outer_r, sector_angle, svg dimensions, volume_ml
- `glass_wrap_path(template)` — SVG path d-attribute for glass outline
- `create_warp_function(template, rect_width, rect_height)` — returns function mapping rect coords to glass polar coords
- `warp_layout(layout, template, padding_opts)` — applies warp to entire layout
- `compute_fill_height(template, volume_ml)` — binary search for liquid fill level

### 3. SVG Renderer (`api/app/services/render/svg.py`)

Port from `public/svg-renderer.js` (~206 lines). Main function: `render_svg(layout, opts)`

**Features to port:**
- Per-hole color coding with hue rotation (18-hole cycle)
- Hue values: `[120,150,90,180,60,200,100,160,75,130,170,80,190,55,210,110,145,85]`
- Category tinting (fairway, rough, tee, green at 35% fill / 25% stroke)
- 9 layer system: background, rough, fairway, water, bunker, tee, green, hole_number, hole_par
- Toggleable layer visibility via hidden_layers set
- Default style dict (copy colors from svg-renderer.js)
- Polygon/polyline rendering for features
- Hole number circles with labels
- Par labels at green centroids
- Logo support (data URL image, rotated -90 deg on left edge)
- Glass/warped mode: clip path, curved text paths
- Font family customization
- SVG string output (no external deps)

### 4. Scoring Zone Service (`api/app/services/render/scoring.py`)

New code (not in old stack — this is Phase 2 prep, but stub it properly):
- `compute_scoring_zones(hole, green_bbox)` — generates zone boundaries
- Zone heights narrow toward green: +5 (widest) down to 0 (thin), then green, then +1/+2 below
- Return zone boundaries as y-coordinates relative to hole layout

For now, create a working stub that returns placeholder zones based on green position. Full implementation is Phase 2.

### 5. Layout + Render API Endpoint

Create a new endpoint for the designer to call:

**`api/app/api/v1/render.py`**:
```
POST /api/v1/render
Body: { holes: [...], options: { canvas_width, canvas_height, glass_count, holes_per_glass, styles, hidden_layers, font_family, logo_url, mode: "rect"|"glass" } }
Returns: { svg: "<svg>...</svg>", layout: { holes: [...], canvasWidth, canvasHeight } }
```

Also:
```
POST /api/v1/render/glass-template
Body: { glass_height, top_radius, bottom_radius, wall_thickness, base_thickness }
Returns: { template: { ...all computed values }, path: "<svg path d>" }
```

Register this router in `api/app/api/router.py`.

### 6. Settings Endpoints (`api/app/api/v1/settings.py`)

Update the stubs to actually work with MongoDB:

- `POST /api/v1/settings` — save design config to `design_settings` collection
  - Body: `{ course_name: str, settings: dict }`
  - Generate filename-style ID: `{course_name}_{ISO_TIMESTAMP}`
  - Return `{ ok: true, id: "..." }`

- `GET /api/v1/settings` — list all saved settings
  - Return array of `{ id, course_name, saved_at }`
  - Sorted newest first

- `GET /api/v1/settings/{setting_id}` — load specific settings
  - Return the full settings document

## Reference Files (READ ONLY — do not modify)
- `/Users/contextuallabs/code/one-nine/public/layout-engine.js`
- `/Users/contextuallabs/code/one-nine/public/svg-renderer.js`
- `/Users/contextuallabs/code/one-nine/public/glass-template.js`
- `/Users/contextuallabs/code/one-nine/server.js` — settings endpoints (lines ~242-300)

## Files to Create/Modify
- MODIFY: `api/app/services/render/layout.py`
- MODIFY: `api/app/services/render/svg.py`
- MODIFY: `api/app/services/render/glass_template.py`
- MODIFY: `api/app/services/render/scoring.py`
- CREATE: `api/app/api/v1/render.py`
- MODIFY: `api/app/api/v1/settings.py`
- MODIFY: `api/app/api/router.py` (add render router)

## Definition of Done
- [ ] Layout engine produces same zigzag positioning as JS version
- [ ] Glass template geometry matches JS version
- [ ] SVG renderer produces valid SVG with all layers and styling
- [ ] Glass warp mode works (curved layout)
- [ ] `POST /api/v1/render` returns SVG string from hole data
- [ ] Settings CRUD works with MongoDB
- [ ] Scoring zones stubbed with placeholder computation

## Done Report
When complete, write your done report to: `coordination/api/outbox/003-done.md`
