# Task 004: Scoring Zones + Ruler (Phase 2)

## Priority: HIGH — core gameplay feature

## Prerequisites
- Phase 1 complete (layout engine, SVG renderer working)

## What to Build

### 1. Full Scoring Zone Computation (`api/app/services/render/scoring.py`)

Replace the placeholder stub with proper scoring zone calculation. Reference the plan's scoring zone spec.

**Per-hole scoring zones (vertical bands around the green):**

```
── +5 zone ──  (widest, furthest above green — toward lip)
── +4 zone ──
── +3 zone ──
── +2 zone ──  (narrowing)
── +1 zone ──  (narrow)
──  0 zone ──  (thin band just outside the green)
┌─ GREEN ─────┐
│   -1        │  ← beer visible through bare glass
└─────────────┘
── +1 zone ──  (small buffer below green)
── +2 zone ──  (can slightly overlap next tee box)
```

**Zone height algorithm:**
- Zones narrow toward the green (exponential or power curve)
- +5 zone is widest (e.g., 25% of available space above green)
- Each zone progressively narrower: +4 (20%), +3 (17%), +2 (15%), +1 (13%), 0 (10%)
- These ratios should be configurable/tunable
- Available space = distance from top of hole's vertical allocation to top of green
- Below green: +1 and +2 zones split remaining space before next hole's tee

**Green interior scoring:**
- Small greens: entire green = -1
- Large greens (above a threshold): inner region near arbitrary hole location = -1, outer = 0
- Threshold: configurable, default based on green area relative to hole height

**Function signature:**
```python
def compute_scoring_zones(
    hole_layout,           # hole from compute_layout output
    available_top: float,  # y-coordinate of top boundary
    available_bottom: float,  # y-coordinate of bottom boundary (next hole's tee or glass bottom)
    zone_ratios: dict | None = None,  # override default narrowing ratios
) -> ScoringZoneResult:
    # Returns zone boundaries as y-coordinates
```

**Output schema** (add to `api/app/schemas/`):
```python
class ScoringZone:
    score: int          # -1, 0, 1, 2, 3, 4, 5
    y_top: float        # top boundary (canvas y)
    y_bottom: float     # bottom boundary (canvas y)
    label: str          # display label
    position: str       # "above" | "green" | "below"

class ScoringZoneResult:
    hole_ref: int
    zones: list[ScoringZone]
    green_y_top: float
    green_y_bottom: float
```

### 2. Ruler Generation

Add ruler rendering to the SVG renderer (`api/app/services/render/svg.py`).

**Ruler specification (from plan):**
- Positioned on the **right edge** of the glass/canvas
- Vertical ruler with:
  - Tick marks at each scoring zone boundary per hole
  - Score labels (-1, 0, 1, 2, 3, 4, 5) at each tick
  - Hole number labels at each section
- White color only (for vinyl cutting)
- Width: ~40px for rect mode, proportional for glass mode

**Implementation:**
- Add `_render_ruler(zones_by_hole, draw_area, opts)` function to svg.py
- Called from `render_svg()` when ruler is enabled
- Ruler should be its own layer (add "ruler" to the layer system)
- Tick marks: small horizontal lines extending left from the ruler edge
- Score labels: right-aligned text next to ticks
- Hole labels: larger text centered in each hole's vertical section

### 3. Scoring Zone Arcs in SVG

Add concentric arc rendering around each green in the SVG.

**Implementation:**
- Add `_render_scoring_arcs(hole, zones, opts)` function to svg.py
- Renders concentric arcs/bands around each green
- White vinyl only (outline arcs, no fill — for Cricut cutting)
- Arc shape follows the green's outline shape, expanded outward
- Each zone boundary = one arc line
- Add "scoring_arcs" to the layer system

### 4. Hole Stats Display

Add par, yardage, handicap labels positioned near each hole.

**Implementation:**
- Add `_render_hole_stats(hole, layout_hole, opts)` to svg.py
- Position in empty space near each hole (avoid overlapping features)
- White text, small font
- Format: "Par 4 · 385 yd · HCP 7"
- Add "hole_stats" to the layer system

### 5. Integrate Zones into Layout + Render Pipeline

- In `compute_layout()` or a post-processing step, compute scoring zones for each hole
- Pass zones to `render_svg()` for arc/ruler rendering
- Update `POST /api/v1/render` to include zone data in response
- Add `scoring-preview` render mode that shows zones with colored bands (for admin/testing)

### 6. Scoring Preview Mode

New render mode `scoring-preview`:
- Same as `rect` mode but with scoring zones visualized
- Each zone rendered as a colored semi-transparent band
- Color coding: -1 = dark green, 0 = light green, 1 = yellow, 2 = orange, 3 = red-orange, 4 = red, 5 = dark red
- Zone labels shown in each band
- Useful for testing and tuning zone heights

## Files to Modify
- MODIFY: `api/app/services/render/scoring.py` (replace stub with full implementation)
- MODIFY: `api/app/services/render/svg.py` (add ruler, scoring arcs, hole stats, scoring-preview mode)
- MODIFY: `api/app/services/render/layout.py` (integrate zone computation)
- MODIFY: `api/app/api/v1/render.py` (add scoring-preview mode, include zones in response)
- CREATE: `api/app/schemas/scoring.py` (ScoringZone, ScoringZoneResult models)

## Definition of Done
- [ ] Scoring zones computed per hole with narrowing widths toward green
- [ ] Ruler renders on right edge with tick marks, score labels, hole numbers
- [ ] Scoring arcs render around greens in white
- [ ] Hole stats (par/yardage/handicap) display near each hole
- [ ] `scoring-preview` mode shows colored zone bands
- [ ] All layers toggleable (ruler, scoring_arcs, hole_stats)
- [ ] Existing rect and glass render modes still work correctly
- [ ] Tests cover zone computation, ruler rendering, new render modes

## Done Report
When complete, write your done report to: `coordination/api/outbox/004-done.md`
