# Glass Preview Overhaul — Realistic 3-Color Rendering + Terrain-Following Scoring Zones

## Summary

The glass preview currently renders a flat green SVG with feature outlines — it looks nothing like the actual vinyl product on a clear glass. This task overhauls the preview to show what the finished glass will actually look like, adds the missing course name and ruler, and makes scoring zones follow the terrain of each hole instead of being simple horizontal bands.

---

## Current Problems

### 1. Preview doesn't represent the physical glass
The current glass-mode preview renders all features as filled colored shapes on a solid dark green background. The actual product is:
- **Clear glass** (no background — beer is visible)
- **White vinyl** outlines (labels, arcs, ruler, hole numbers, stats)
- **Green vinyl** pieces (green outlines with hollow interiors, tee boxes)
- **Tan vinyl** pieces (bunker shapes)
- Everything else is bare glass

The preview should show: transparent/dark background representing clear glass, white stroked outlines for most elements, green stroked shapes for greens/tees, tan filled shapes for bunkers. The green interiors should be visually distinct (cutout/transparent) since beer is visible through them.

### 2. Course name missing from glass preview
`plan.md` specifies:
- Course name runs **vertically up the left side** (first letter at bottom, last at top)
- Below it: hole range ("Holes 1–6"), same vertical orientation reading bottom-to-top
- Font: sourced from course website if available, fallback to all-caps display font

The current `render_svg()` has text rendering for rect/glass modes (`_render_warped_text` and `_render_rect_text` in svg.py) but:
- In glass mode, course name is along a curved textArc — should be a straight vertical line on the left edge of the glass wrap
- The text reads along the arc, not bottom-to-top vertically
- Font hint system exists (`font_hints.py`) but isn't reflected visually yet

### 3. Ruler missing from glass preview
The ruler renders in rect mode only (svg.py `_render_ruler()`). It's completely absent in glass/warped mode. The plan requires it on the far right side of the glass, opposite the course name, with tick marks and score labels for each hole.

### 4. Scoring zones are horizontal bands, not terrain-following
Current scoring zones (`scoring.py`) compute simple `y_top`/`y_bottom` bands. These render as:
- Horizontal colored rectangles in `scoring-preview` mode
- Concentric circles (arcs) around the green centroid in normal mode

The user wants zones that **follow the terrain**:
- **-1 zone**: follows the actual green shape (the green outline itself)
- **0 zone**: thin band just outside the green, roughly following the green's contour
- **+1 zone**: extends outward, following rough/fairway boundary near the green
- **+2, +3, etc.**: progressively wider bands that increasingly approximate horizontal (further from terrain, more geometric)

This means zones are **contour offsets** of the green shape, not simple horizontal slices.

### 5. One Nine logo only at the bottom
Logo should appear only at the bottom-left of the glass, near the base. Currently the logo placement is a stub.

---

## Required Changes

### A. New Preview Mode: "vinyl-preview"
Add a new rendering mode that simulates the actual glass appearance:

**Background**: Dark/transparent gradient simulating clear glass with beer inside
**White elements** (stroked, no fill):
- Feature outlines (fairway, rough, water boundaries)
- Scoring zone arcs/contours
- Hole numbers (circle + number)
- Hole stats text (Par, yardage, handicap)
- Ruler (right side)
- Course name + hole range (left side, vertical)

**Green elements** (stroked, hollow interior):
- Green outlines — interior should look transparent/amber (beer visible)
- Tee box shapes
- Fairway accent outlines

**Tan elements** (filled):
- Bunker shapes

**Visual treatment**:
- Green interiors: render as a slightly brighter/amber region to simulate beer showing through
- White elements: crisp white strokes on dark background
- Transparency between elements (bare glass = dark background showing through)

### B. Course Name — Vertical Left Strip
In `svg.py`, for both rect and glass modes:
- Position course name as vertical text on the left edge
- Text reads bottom-to-top (first letter at bottom, last at top)
- Use `transform="rotate(-90)"` with appropriate translate
- Below it (further left or slightly overlapping): "Holes X–Y" in smaller text, same orientation
- Font: use `font_hint` from course data if available, fall back to configured `font_family`
- White color, bold, ~12pt for rect / ~7pt for glass

### C. Ruler — Right Edge (All Modes)
Extend `_render_ruler()` to work in glass/warped mode:
- For rect mode: current implementation is fine (right edge, vertical line + ticks)
- For glass mode: ruler should be along the right edge of the glass wrap sector
  - Tick marks and labels follow the curved right edge
  - Each hole section has score labels (-1, 0, +1...+5)
  - Hole number dividers between sections

### D. Terrain-Following Scoring Zones
Replace the current geometric zone computation with contour-based zones:

**Algorithm:**
1. For each hole, extract the green feature polygon(s)
2. Compute the green centroid and bounding shape
3. Generate concentric offset contours:
   - **-1 zone**: the green polygon itself
   - **0 zone**: offset the green polygon outward by a small amount (2-3px)
   - **+1 zone**: offset further, blending toward nearby rough/fairway features
   - **+2 through +5**: progressively larger offsets that increasingly become horizontal bands (lerp between terrain contour and simple horizontal line)
4. The vertical extent of each zone still narrows toward the green (same ratio system)
5. Zones should NOT bleed past the next hole's tee box

**Rendering:**
- In `scoring-preview` mode: filled colored bands using contour shapes
- In `vinyl-preview` / normal mode: white stroked arc/contour outlines
- On the ruler: horizontal tick marks at the Y-center of each zone (these remain horizontal — ruler is geometric)

**Implementation approach:**
- In `scoring.py`: add a `compute_terrain_zones()` function that takes hole features + layout and returns polygon outlines per zone (not just y_top/y_bottom)
- Start simple: use elliptical offsets around the green centroid, elongated along the hole routing direction
- Phase 2: true polygon offset using the green + surrounding feature shapes

### E. Logo Placement
- One Nine logo: bottom-left of the glass, small, near the base
- In glass mode: near the inner arc (bottom of glass wrap)
- White vinyl (or embedded as-is if it's the white-on-transparent PNG)

---

## Files to Modify

### Backend
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Add `vinyl-preview` mode, fix course name positioning (vertical bottom-to-top), extend ruler to glass mode, render terrain-following zone contours, logo placement |
| `api/app/services/render/scoring.py` | Add `compute_terrain_zones()` returning polygon outlines per zone instead of just y_top/y_bottom. Keep existing `compute_scoring_zones()` as fallback. |
| `api/app/api/v1/render.py` | Pass new mode through, ensure terrain zones computed when needed |

### Frontend
| File | Changes |
|------|---------|
| `frontend/src/stores/designer.ts` | Add 'vinyl-preview' to `previewMode` type, make it the default mode |
| `frontend/src/views/DesignerView.vue` | Add "Vinyl" mode button in toolbar, possibly make it default |

---

## Acceptance Criteria

1. **Selecting a course in the designer shows a realistic glass preview** — clear glass background, white/green/tan vinyl elements visible, green interiors appear transparent
2. **Course name** appears vertically on the left, reading bottom-to-top, with hole range below it
3. **Ruler** appears on the right side in all modes (rect and glass), with tick marks and score labels per hole
4. **Scoring zones** follow the terrain of the green in the -1 through +1 range, progressively becoming more horizontal for +2 through +5
5. **One Nine logo** appears only at the bottom-left of the glass
6. The existing `rect`, `glass`, `scoring-preview`, and `cricut-*` modes continue to work unchanged
7. `vinyl-preview` becomes the default preview mode in the designer

---

## Priority

**High** — This is the primary visual feedback loop for the designer. Without a realistic preview, it's impossible to judge how the final glass will look.
