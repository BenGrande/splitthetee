# Task 020: Print Accuracy (Remove Glow/Fills) + Thinner Outlines (Phase A)

**Priority**: Critical
**Depends on**: Nothing

**IMPORTANT**: Before marking done, render a real course SVG and visually inspect it. Verify BOTH rect and glass modes.

---

## Part 1: Remove Fake Green Glow + Concentric Shapes (Issue 8)

### The Rule
**The glass preview must show ONLY what will physically be printed.** Four vinyl colors (white, blue, green, tan) on a transparent/dark background. No glows, no fake transparency effects, no simulation of beer.

### Changes in `svg.py` — `_render_vinyl_preview()`

**A. Remove amber glow around greens:**
- Find and remove the `rgba(255,180,50,0.15)` fill that renders under green features (approximately line ~510-521)
- Green outlines = green stroke on dark background, nothing more

**B. Remove terrain zone contour FILLS:**
- In `_render_terrain_zones()`: when rendering for vinyl mode, zones must ONLY be white stroke boundaries (the lines between zones)
- Remove any `fill` on terrain zone polygons — no filled zone shapes should be visible
- Zone boundary LINES are white strokes (these ARE printed as scoring zone markers)
- Filled zone polygons that create concentric colored shapes must be removed

**C. Background:**
- Keep the dark background (represents clear glass)
- Do NOT simulate beer color — just use a solid dark background (`#1a1a1a` or `#111111`)
- Remove any gradient that simulates beer (`beerGrad` etc.)

**D. Verify print accuracy — every visible element must correspond to a vinyl cut:**
- White elements = white vinyl
- Green elements = green vinyl (outlines only — interiors are bare glass)
- Blue elements = blue vinyl (filled)
- Tan elements = tan vinyl (filled)
- NOTHING ELSE

## Part 2: Thinner Outlines (Issue 6)

### Changes in `svg.py`
Reduce vinyl preview stroke widths:
- White features (rough/path/course_boundary): **0.4** (was 0.8)
- Green outlines: **0.6** (was 1.0)
- Water outlines (around filled blue): **0.2** (was 0.8) — fill defines shape, stroke is minimal
- Fairway (filled green): stroke **0.2** — fill defines shape
- Scoring zone boundary lines: **0.3**

### Changes in `cricut.py`
- Match reduced stroke widths in cricut white layer

## Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Remove amber glow, remove terrain zone fills (keep boundary strokes only), remove beer gradient, reduce all stroke widths |
| `api/app/services/render/cricut.py` | Reduce stroke widths to match |

## Definition of Done
1. No amber glow around greens
2. No concentric filled shapes around greens
3. No beer-simulating gradient background (solid dark background)
4. Only printed elements visible: white/green/blue/tan vinyl on dark bg
5. Outlines are thin and clean
6. Visually verified in BOTH rect and glass modes with a real course
7. All tests pass
