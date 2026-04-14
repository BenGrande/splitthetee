# Task 012: Add Blue Vinyl Color for Water Hazards

**Priority**: High
**Depends on**: Task 011 (clean baseline)

---

## Overview
Water hazards are currently rendered as white outlines (same as fairway). They should be a distinct **blue** vinyl color (`#3b82f6`). This expands the vinyl palette from 3 to 4 colors.

## Changes Required

### 1. SVG Renderer — Water in Blue
In `svg.py`, wherever features are categorized and rendered:
- Features with `category === "water"` (or type containing "water") should render in blue (`#3b82f6`) instead of white
- Applies to ALL rendering modes:
  - `rect` mode: blue stroked outlines
  - `glass` mode: blue stroked outlines
  - `vinyl-preview` mode: blue stroked/filled shapes
  - `scoring-preview` mode: blue features

### 2. Cricut Export — New Blue Layer
In `cricut.py`:
- Add `render_cricut_blue(layout, opts)` function
  - Extracts all water hazard features from the layout
  - Renders them as cut paths (same pattern as `render_cricut_green()` and `render_cricut_tan()`)
  - Compact arrangement for efficient cutting
  - Blue color (`#3b82f6`) for the SVG
- Update `render_cricut_guide()` to show water in blue on the placement guide

### 3. Render API — Blue Layer Endpoint
In `render.py`:
- Add `cricut-blue` as a valid mode
- Update `cricut-all` response to include `blue` key alongside `white`, `green`, `tan`
- Response shape becomes: `{ white: "...", blue: "...", green: "...", tan: "..." }`

### Water Feature Detection
Check how water features are currently categorized in the layout data. Look at:
- `api/app/services/golf/holes.py` — how OSM features are categorized
- Feature types that indicate water: `water`, `water_hazard`, `lake`, `pond`, `stream`, `river`, `canal`
- The layout engine should already tag these; just need to use the tag for color routing

## Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Route water features to blue color in all render modes |
| `api/app/services/render/cricut.py` | Add `render_cricut_blue()`; update `render_cricut_guide()` |
| `api/app/api/v1/render.py` | Add `cricut-blue` mode; update `cricut-all` to include blue |

## Definition of Done
1. Water hazards render in blue (`#3b82f6`) in all SVG modes (rect, glass, vinyl-preview, scoring-preview)
2. `render_cricut_blue()` produces valid SVG with water hazard cut paths
3. `/api/v1/render/cricut` with mode `cricut-blue` returns blue layer SVG
4. `cricut-all` response includes `blue` key with valid SVG
5. Non-water features unchanged (still white/green/tan as before)
6. All existing tests pass + new tests for blue rendering and cricut blue layer
