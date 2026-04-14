# Comprehensive Fix Plan — Export, Vinyl, Glass View, Scoring Zones, Ruler, Blue Vinyl

**Date**: 2026-04-13
**Priority**: Critical — these issues block the product from being usable

**Supersedes**: `glass-preview-overhaul.md`, `ruler-readability-fix.md` (this plan incorporates and expands both)

---

## Issue 1: Export Functionality Broken (SVG + ZIP)

### Problem
Both SVG and ZIP downloads produce empty/corrupt files. The Vue frontend triggers the download but the resulting files are unusable.

### Root Cause Investigation
The frontend export flow in `frontend/src/stores/designer.ts`:
- `exportSvg()` (line ~199): Creates blob from `currentSvg.value` and triggers download via `<a>` tag
- `exportAllSvg()` (line ~211): Loops through glasses, renders each, zips into a single file
- `exportCricut()` (line ~267): POSTs to `/api/v1/render/cricut`, stores response SVGs
- `downloadCricutLayer()` / `downloadAllCricutLayers()`: Downloads individual or zipped cricut layers

Likely failure points:
1. `currentSvg.value` may be empty/null when export is triggered (render hasn't completed or failed silently)
2. The blob MIME type or encoding may be wrong
3. The ZIP library (JSZip) may not be properly imported or awaited
4. The `/api/v1/render/cricut` endpoint may be returning errors that aren't surfaced to the user
5. CORS or content-type headers may strip the response body

### Required Fix
1. **Debug the export pipeline end-to-end**: Add error handling and console logging at each step
2. **Verify SVG content exists** before creating blob — show user error if empty
3. **Verify ZIP library** is properly imported and `generateAsync()` is awaited
4. **Verify API response** for cricut endpoint — check response status, content-type, body
5. **Test each export path**: single SVG, all SVGs ZIP, cricut single layer, cricut all layers ZIP

### Files to Modify
| File | Changes |
|------|---------|
| `frontend/src/stores/designer.ts` | Fix `exportSvg()`, `exportAllSvg()`, `exportCricut()`, `downloadCricutLayer()`, `downloadAllCricutLayers()` — add error handling, verify content before download |
| `frontend/src/components/CricutExportPanel.vue` | Surface errors to user, disable buttons when no content |
| `api/app/api/v1/render.py` | Verify render and cricut endpoints return valid SVG, add error responses |

---

## Issue 2: Vinyl Preview Has Weird Horizontal Lines

### Problem
The vinyl preview mode shows random horizontal lines across the glass.

### Root Cause
These are **terrain zone contours** rendered in `_render_vinyl_preview()` in `svg.py` (around line 428-443):
```python
if terrain_zones:
    for hole_tzs in terrain_zones:
        for tz in hole_tzs:
            contour = tz.get("contour", [])
            d = _coords_to_path(contour, closed=True)
            svg += f'<path d="{d}" fill="none" stroke="#ffffff" stroke-width="0.5" opacity="0.3"/>'
```

The terrain zone contour computation in `scoring.py` (`compute_terrain_zones()`) generates polygon outlines that, when rendered as closed paths, create stray horizontal lines — likely because the contour algorithm produces degenerate or poorly-shaped polygons (e.g., very thin horizontal slivers).

### Required Fix
1. **Remove the current terrain zone contour rendering** from the vinyl preview — it's producing visual artifacts
2. **Replace with the new terrain-following scoring zone system** (see Issue 4 below) once implemented
3. Until the new system is ready, scoring zones in vinyl preview should use the simple zone boundary lines (horizontal ticks at zone boundaries) rather than full contour polygons

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Remove/disable terrain zone contour rendering in vinyl preview; replace with new zone system |
| `api/app/services/render/scoring.py` | Fix or replace `compute_terrain_zones()` |

---

## Issue 3: Glass View Should Show Exact Print Output

### Problem
The glass view doesn't match what will actually be printed on the glass. It needs to show the exact vinyl layout — white, blue, green, and tan elements on a clear glass background — in the warped/arched glass shape. The bulls-eye concentric circles around greens need to be replaced with the new terrain-following zones.

### Current State
- Glass mode renders features as colored fills on dark green background
- Vinyl preview mode exists but has the horizontal line artifacts (Issue 2)
- Scoring arcs are concentric circles (`_render_scoring_arcs()`) — look like bulls-eyes

### Required Changes
The glass preview should be the **definitive "what you'll get" view**:

1. **Background**: Dark amber gradient simulating beer in clear glass
2. **White vinyl elements** (white strokes):
   - Feature outlines (fairway, rough, water boundaries — except water is now blue, see Issue 6)
   - Scoring zone boundaries (terrain-following, see Issue 4)
   - Score numbers inside/outside zones with leader lines
   - Hole number circles with dashed lines to tee boxes (Issue 7)
   - Hole stats text (par, yardage)
   - Ruler on right edge
   - Course name on left edge (vertical, bottom-to-top)
   - Logo at bottom
3. **Blue vinyl elements** (blue strokes/fills):
   - Water hazard shapes
4. **Green vinyl elements** (green strokes, hollow interior):
   - Green outlines (interior = bare glass = beer visible = amber glow)
   - Tee box shapes
   - Fairway accent outlines
5. **Tan vinyl elements** (tan fills):
   - Bunker shapes
6. **Remove bulls-eye circles** — replace `_render_scoring_arcs()` with the new terrain-following zone rendering

### Glass Outline
- Warped to pint glass sector shape
- Clipped to glass outline
- Glass outline visible as reference

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Overhaul `_render_vinyl_preview()` to be the canonical glass view; remove `_render_scoring_arcs()` bulls-eye circles; add blue water rendering; ensure all print elements present |
| `api/app/services/render/cricut.py` | Add blue layer (`render_cricut_blue()`) for water hazards; update `render_cricut_white()` to exclude water (now blue); update `render_cricut_guide()` |
| `api/app/api/v1/render.py` | Add `cricut-blue` mode; update `cricut-all` to include blue layer |

---

## Issue 4: Terrain-Following Scoring Zones

### Problem
Current scoring zones are horizontal bands (y_top/y_bottom). The user wants zones that follow the actual course terrain, radiating outward from the green along the fairway.

### New Zone System

**Zone layout (from green outward toward tee):**

| Zone | Score | Location | Description |
|------|-------|----------|-------------|
| Green interior | -1 or 0 | Inside the green polygon | -1 for small greens (entire interior), or -1 near hole / 0 outer for large greens |
| Zone 0 | 0 | Thin band immediately around green | Follows green contour shape |
| Zone +1 | +1 | Area around the 0 zone | Still roughly follows green shape, slightly more geometric |
| Zone +2 | +2 | On the fairway, near green | Follows fairway shape |
| Zone +3 | +3 | On the fairway, mid-hole | Follows fairway shape |
| Zone +4 | +4 | On the fairway, near tee | Follows fairway shape |
| Zone +5 | +5 | On the fairway, at/near tee | Widest zone |

**Key design principles:**
- Zones radiate **outward from the green** along the fairway/hole routing
- Near the green, zones follow the green's contour shape
- Further from the green, zones increasingly follow the fairway shape
- Each zone is a band between two contour lines
- Zones get wider further from the green (more forgiveness for worse scores)

### Score Number Labels
- Each zone displays its score as a **small white number**
- If the zone is large enough: number placed **inside** the zone
- If the zone is too small: number placed **outside** with a **dotted leader line** connecting the number to the zone it represents
- Numbers should be legible but unobtrusive (~4-5px font in glass mode)

### Algorithm
1. For each hole, get the green polygon and the fairway polygon(s)
2. Compute the hole routing line (tee → green path)
3. Generate zone boundaries as **offset contours**:
   - -1/0: offset outward from green polygon edge
   - +1: further offset, blending toward fairway edges
   - +2 through +5: divide remaining fairway length into proportional bands along the routing line, following fairway width
4. Each zone boundary is a polygon/path (not just a y-coordinate)
5. Zone width ratios still apply (narrower near green, wider near tee)
6. Zones must not extend past the next hole's tee box area

### Rendering
- **Glass/vinyl preview**: White stroked contour lines at zone boundaries; white score numbers inside or with leader lines
- **Scoring preview mode**: Semi-transparent colored fills inside each zone polygon
- **Cricut white layer**: Zone boundary lines as cut paths; score numbers as cut text
- **Ruler**: Horizontal tick marks at the Y-center of each zone (ruler remains geometric/horizontal)

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/scoring.py` | Rewrite zone computation: `compute_terrain_following_zones()` that returns polygon contours per zone, not just y_top/y_bottom. Keep old functions as fallback. |
| `api/app/services/render/svg.py` | New zone rendering function that draws contour-based zones with score labels + leader lines. Replace `_render_scoring_arcs()`. |
| `api/app/services/render/cricut.py` | Update white layer to include new zone contours + score labels |

---

## Issue 5: Ruler Readability Overhaul

### Problem
The ruler is too hard to read. Zone boundaries aren't clear, hole numbers clutter the score area.

### Required Changes

#### A. Tick marks on BOTH sides of the ruler spine
Every zone boundary gets a tick mark extending **left AND right** of the vertical ruler line. This makes it unambiguous where each zone starts and ends — you can trace horizontally across the glass from either side.

#### B. Hole numbers moved to LEFT side of ruler
Hole numbers are relocated from inline with scores to a **vertical strip on the left edge of the ruler area**.

**Layout:**
- Each hole gets a rectangular cell in a vertical column
- **Odd-numbered holes** (1, 3, 5...): White filled rectangle with the hole number **cut out** (knocked out of white — number is clear/bare glass)
- **Even-numbered holes** (2, 4, 6...): White outline rectangle (no fill) with the hole number rendered in **white** inside
- Hole numbers are **rotated 90 degrees** (sideways) inside these rectangles
- Rectangles alternate white-fill / clear-outline pattern for easy visual scanning

#### C. Score labels
- Score labels (-1, 0, 1, 2, 3, 4, 5) remain next to the tick marks
- Labels should be clearly sized (8pt minimum in rect mode)
- Alternating left/right stagger (from existing ruler-readability-fix.md) to prevent overlap
- Zone range visible via alternating subtle background bands

#### D. Zone range brackets
- Thin vertical bracket or highlighted spine segment spanning each zone's full extent
- Alternating opacity to distinguish adjacent zones

### Visual Reference
```
 ┌──────┐  ─── +5 ───────  ← ticks on BOTH sides
 │  1   │  ─── +4 ───────
 │(side)│  ─── +3 ───────
 └──────┘  ─── +2 ───────
 ┌──────┐  ─── +1 ───────
 │      │  ─── 0  ───────
 │  2   │  ─── -1 ───────  (green zone)
 │      │  ─── +1 ───────  (below-green)
 └──────┘
```

Left column: alternating white-filled/outline rectangles with sideways hole numbers.
Right column: ruler spine with dual-side ticks and score labels.

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Rewrite `_render_ruler()` and `_render_ruler_warped()` — move hole numbers to left column with alternating rectangles, add dual-side ticks, improve label sizing and collision handling |
| `api/app/services/render/cricut.py` | Update ruler in `render_cricut_white()` to match new design |

---

## Issue 6: Add Blue Vinyl Color (Water Hazards)

### Problem
Water hazards are currently rendered as white outlines (same as fairway). They should be a distinct **blue** vinyl color.

### Changes
The vinyl color palette expands from 3 to 4 colors:

| Color | Vinyl | Used For |
|-------|-------|----------|
| **White** | White vinyl | Outlines, labels, ruler, scoring zone lines, hole numbers, stats, brand, QR |
| **Blue** | Blue vinyl | Water hazard shapes |
| **Green** | Green vinyl | Green outlines (hollow interior), tee boxes, fairway accents |
| **Tan** | Tan vinyl | Bunker shapes |

### Implementation
1. **SVG renderer**: Water features (`category === "water"`) rendered in blue (`#3b82f6` or similar) instead of white
2. **Cricut export**: New `render_cricut_blue()` function for blue layer — compact arrangement of water hazard shapes, same pattern as green/tan layers
3. **Cricut all**: Include blue layer in the `cricut-all` bundle
4. **Vinyl preview**: Water rendered as blue strokes/fills on the glass preview
5. **Guide layer**: Water shown in blue on the placement guide

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Render water features in blue in all modes |
| `api/app/services/render/cricut.py` | Add `render_cricut_blue()`; update `render_cricut_guide()` |
| `api/app/api/v1/render.py` | Add `cricut-blue` mode; update `cricut-all` response to include blue |
| `frontend/src/components/CricutExportPanel.vue` | Add blue layer to export panel UI |
| `frontend/src/stores/designer.ts` | Handle blue layer in cricut export/download |

---

## Issue 7: Dashed Lines from Hole Number to Tee Box

### Problem
There's no visual connection between the hole number circle and its tee box on the course. Players can't easily tell which tee belongs to which hole.

### Required Change
Draw a **dashed line** from each hole number circle to the corresponding tee box:
- Line starts at the hole number circle (which is positioned near each hole)
- Line ends at the tee box feature
- Style: white, dashed (`stroke-dasharray`), thin (0.5-1px)
- Should be subtle enough not to clutter but visible enough to trace

### Implementation
In the SVG renderer, after rendering hole number circles and tee features:
1. For each hole, find the hole number circle position and the tee box centroid
2. Draw a dashed white line connecting them
3. In glass/warped mode, the line follows the warp transformation

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Add dashed line rendering from hole number to tee box in all relevant modes |
| `api/app/services/render/cricut.py` | Include dashed lines in white cricut layer |

---

## Implementation Order

These issues have dependencies. Recommended order:

### Phase A: Foundation Fixes (unblocks everything else)
1. **Issue 1: Fix export** — quick win, unblocks testing of all other changes
2. **Issue 2: Remove terrain zone artifacts** — removes visual noise so we can see other changes clearly

### Phase B: Core Rendering Overhaul
3. **Issue 6: Add blue vinyl** — simple color addition, needed before the glass view overhaul
4. **Issue 4: Terrain-following scoring zones** — core algorithm change, needed for glass view and ruler
5. **Issue 3: Glass view = exact print output** — depends on blue vinyl + new zones being implemented

### Phase C: Polish
6. **Issue 5: Ruler overhaul** — depends on new zone system for accurate zone boundaries
7. **Issue 7: Dashed lines hole number → tee** — independent, can be done anytime after Phase A

---

## Acceptance Criteria

1. **Export works**: SVG downloads contain valid SVG. ZIP downloads contain multiple valid SVGs. Cricut layers download correctly.
2. **No stray lines**: Vinyl preview is clean — no random horizontal lines or visual artifacts.
3. **Glass view = print output**: Glass preview shows exactly what will be printed — white, blue, green, tan elements on amber/clear background, warped to glass shape. All elements present: course name, ruler, zones, hole numbers, stats, logo.
4. **Scoring zones follow terrain**: Zones radiate from green along fairway. Score numbers visible in/near each zone. Leader lines for small zones.
5. **Ruler is readable**: Ticks on both sides. Hole numbers on left in alternating white/clear sideways rectangles. Clear zone boundaries. No overlapping labels.
6. **Blue water**: Water hazards render in blue across all modes. Blue cricut layer available for export.
7. **Hole number → tee dashes**: Each hole number circle has a dashed line to its tee box.
