# Task 014: Glass View = Exact Print Output

**Priority**: High
**Depends on**: Task 012 (blue vinyl), Task 013 (terrain zones)

---

## Overview
Overhaul the glass/vinyl preview to be the **definitive "what you'll get" view** — showing exactly what will be printed as vinyl on the glass.

## Current State
- `_render_vinyl_preview()` exists but had artifact issues (fixed in Task 011)
- Glass mode renders features as colored fills on dark green background (wrong)
- Need to unify glass + vinyl-preview into one canonical "this is what you get" view

## Required Rendering

### Background
Dark amber gradient simulating beer in clear glass:
- Top: lighter amber (glass nearly full)
- Bottom: darker amber
- Colors: `#4a3520` → `#2a1f0e` (or similar warm amber tones)

### White Vinyl Elements (white strokes, no fill)
- Feature outlines: fairway, rough, course boundaries
- Scoring zone boundaries (terrain-following contours from Task 013)
- Score numbers with leader lines (from Task 013)
- Hole number circles with number inside
- Hole stats text (Par X, XXX yd)
- Ruler on right edge (full ruler with ticks and labels)
- Course name on left edge (vertical, bottom-to-top, `rotate(-90)`)
- "Holes X–Y" below course name
- One Nine logo at bottom-left
- QR code placeholder at bottom

### Blue Vinyl Elements (blue `#3b82f6` strokes/fills)
- Water hazard shapes (from Task 012)

### Green Vinyl Elements (green `#4ade80` strokes, hollow interior)
- Green outlines — interior rendered as amber glow (beer visible through cutout)
- Tee box shapes
- Fairway accent outlines

### Tan Vinyl Elements (tan `#d2b48c` fills)
- Bunker shapes

### Dashed Lines: Hole Number → Tee Box (Issue 7)
- For each hole: thin white dashed line from hole number circle to tee box centroid
- Style: `stroke="#ffffff" stroke-dasharray="2,2" stroke-width="0.5"`
- In warped mode, line follows the warp transformation

### Glass Outline (warped mode)
- Glass shape visible as reference outline
- Content clipped to glass boundary
- Warped to pint glass sector shape

## Implementation

### Make Vinyl Preview the Canonical Glass View
- When mode is `glass` or `vinyl-preview`, use the same rendering path
- The old `glass` mode fill-based rendering should be replaced
- Keep `rect` mode as a flat/unwrapped alternative

### Ensure ALL Elements Present
Check that every element listed above is actually rendered. The current vinyl preview may be missing some:
- [ ] Course name (vertical, left)
- [ ] Hole range text
- [ ] Ruler (right edge, with all improvements from Task 010)
- [ ] Hole number circles
- [ ] Hole stats (par, yardage)
- [ ] Dashed lines (hole number → tee) — NEW
- [ ] Terrain-following zone contours with score labels
- [ ] Logo (bottom-left)
- [ ] QR code placeholder

## Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Overhaul `_render_vinyl_preview()` to include ALL elements; make glass mode use vinyl preview rendering; add dashed lines from hole numbers to tees; ensure blue water rendering |
| `api/app/services/render/cricut.py` | Add dashed lines to white cricut layer |

## Definition of Done
1. Glass/vinyl-preview shows beer-amber background with white/blue/green/tan vinyl elements
2. ALL elements present: course name, ruler, zones, hole numbers, stats, dashed lines, logo
3. Green interiors show amber glow (beer visible)
4. Water hazards in blue
5. Dashed lines connect each hole number to its tee box
6. Warped mode clips to glass shape
7. No visual artifacts or stray lines
8. All existing tests pass + new tests
