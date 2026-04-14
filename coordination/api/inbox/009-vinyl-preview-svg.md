# Task 009: Vinyl Preview Mode + Course Name + Ruler + Logo in SVG Renderer

## Priority: HIGH
## Depends on: 008 (terrain scoring zones)
## Phase: Post-Phase 5 enhancement

## Summary
Add a new `vinyl-preview` rendering mode to svg.py that simulates the actual 3-color vinyl glass appearance. Also fix course name positioning (vertical left strip), extend ruler to glass mode, and fix logo placement.

## File to Modify
`api/app/services/render/svg.py` (primary)

## Requirements

### A. New `vinyl-preview` Mode
Add handling for `mode == "vinyl-preview"` in `render_svg()`:

**Background:**
- Dark gradient background simulating clear glass with beer inside
- Use a vertical gradient: darker amber at top (fuller), lighter amber at bottom, or a solid dark amber (#2a1f0e or similar)
- In glass/warped mode: apply the gradient to the glass shape clip area

**White elements (stroke only, no fill, color: #ffffff, stroke-width: 0.8-1.2px):**
- Feature outlines for fairway, rough, water, path, course_boundary categories
- Scoring zone contour outlines (from terrain zones — Task 008)
- Hole numbers (circle + number)
- Hole stats text (Par, yardage, handicap)
- Ruler (right side)
- Course name + hole range (left side)

**Green elements (stroke only, hollow interior, color: #4ade80 or similar green):**
- Green outlines — interior should NOT be filled (bare glass / beer visible)
- Tee box shapes — stroked green outlines
- Fairway accent outlines (if any)

**Tan elements (filled, color: #d2b48c or similar tan):**
- Bunker shapes — filled tan

**Green interior treatment:**
- Render green interiors as a slightly brighter/amber region (e.g., semi-transparent overlay rgba(255, 180, 50, 0.15)) to simulate beer showing through the cutout
- This goes UNDER the green stroke outline

**Key difference from existing modes:**
- Most elements are stroke-only (no fill) — simulates vinyl cut outlines
- Background is dark (simulates looking through glass with beer)
- Very different visual feel from the current filled-polygon style

### B. Course Name — Vertical Left Strip
Fix text rendering for BOTH rect and glass modes:

**Rect mode:**
- Course name as vertical text on the left edge of the SVG
- Text reads bottom-to-top: use `transform="rotate(-90)"` with `text-anchor="start"` positioned at bottom-left
- X position: ~10-15px from left edge
- Y position: centered vertically in the course area
- Font: use `font_hint` from course data if available in render options, fall back to configured `font_family`
- White color (#ffffff), bold, font-size ~12px
- Below the course name (same vertical strip, slightly to the right or with spacing): "Holes X–Y" in smaller text (~9px), same orientation

**Glass/warped mode:**
- Course name along the LEFT edge of the glass wrap sector
- Text should follow a straight vertical line (NOT along the curved arc)
- Use a `<text>` with `writing-mode="tb"` or `transform="rotate(-90)"` positioned along the inner-left edge
- "Holes X–Y" below it in smaller text
- Font-size ~7px for glass mode (smaller due to warped scale)

### C. Ruler — Right Edge in Glass Mode
The current `_render_ruler()` only works in rect mode. Extend it:

**Rect mode** (keep existing):
- Vertical line on the right edge, tick marks, score labels

**Glass/warped mode** (new):
- Ruler along the RIGHT edge of the glass wrap sector
- Vertical line following the right edge of the annulus sector
- For each hole section:
  - Tick marks extending inward from the right edge
  - Score labels (-1, 0, +1, +2, +3, +4, +5) at appropriate Y positions
  - Hole number label (H1, H2, etc.) at the top of each section
- Tick positions: map the y_center of each scoring zone through the warp function to get polar coordinates, then draw tick marks along the outer arc edge
- Labels: small text (~5px) positioned just inside the ticks
- White color, thin strokes (0.5px)

### D. Logo Placement
- One Nine logo: bottom-left of the glass layout area, small
- In rect mode: bottom-left corner, ~20x20px, white
- In glass mode: near the inner arc (bottom of glass wrap), left side
- Load from `public/logo.png` (base64 encoded — use the existing logo endpoint/caching from Task 007)
- Only render if logo data is available (graceful skip if not)

### E. Mode Routing
In `render_svg()`, add the `vinyl-preview` case:
```python
if mode == "vinyl-preview":
    # Use dark amber background
    # Render features as strokes (white/green/tan based on category)
    # Render terrain zone contours as white strokes
    # Render ruler, course name, hole stats, logo
```

The existing modes (`rect`, `glass`, `scoring-preview`, `cricut-*`) must remain unchanged.

## Tests
- Test vinyl-preview mode produces SVG with dark background
- Test that green features have stroke but no fill (or amber fill for interior)
- Test that white elements use stroke-only rendering
- Test course name appears as vertical text with rotate transform
- Test ruler renders in glass mode (has tick marks and labels)
- Test logo element present at bottom-left
- Test that existing modes still produce identical output (regression)

## Definition of Done
- [ ] `vinyl-preview` mode renders a realistic 3-color glass simulation
- [ ] Course name appears vertically on left, reading bottom-to-top, in both rect and glass modes
- [ ] Ruler appears on right side in glass/warped mode with tick marks and score labels
- [ ] Terrain zone contours from Task 008 rendered as white stroke outlines
- [ ] Logo placed at bottom-left of glass
- [ ] Existing modes (`rect`, `glass`, `scoring-preview`, `cricut-*`) unchanged
- [ ] All existing tests pass
- [ ] New tests for vinyl-preview, course name, ruler, logo pass
