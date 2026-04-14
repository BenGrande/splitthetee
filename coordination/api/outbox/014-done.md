# Task 014: Glass View = Exact Print Output — DONE

## Summary
Overhauled glass mode to use vinyl-preview rendering as the canonical "what you'll get" view. Added dashed lines from hole numbers to tee boxes. Ensured all elements present including QR code.

## Changes

### 1. Unified Glass + Vinyl Preview (render.py)
- Glass mode (`mode: "glass"`) now sets `vinyl_preview = True` so it uses the same rendering path as `vinyl-preview`
- Glass mode now computes terrain-following zones (previously only computed for vinyl-preview/scoring-preview)
- Glass mode now shows: dark amber background, white/green/blue/tan vinyl elements, terrain zones, all labels
- The old glass mode (colored fills on dark green) is replaced by the vinyl preview renderer

### 2. Dashed Lines: Hole Number → Tee Box (svg.py, cricut.py)
- **svg.py**: New `layer-hole_tee_lines` group in `_render_vinyl_preview()`
  - Thin white dashed line from each hole number circle to tee box centroid
  - Style: `stroke="#ffffff" stroke-dasharray="2,2" stroke-width="0.5" opacity="0.4"`
- **cricut.py**: Same dashed lines added to white cricut layer for cutting

### 3. All Elements Verified Present in Vinyl Preview
- Background: dark amber beer gradient (`beerGrad`) ✓
- Terrain zone contours (white strokes + score labels) ✓
- Green interior amber glow ✓
- Feature layers: white (fairway/rough), green (green/tee), blue (water), tan (bunker) ✓
- Hole number circles ✓
- Dashed lines (hole number → tee) — NEW ✓
- Hole stats (par, yardage) ✓
- Ruler (right edge, rect and warped) ✓
- Course name (vertical, left edge) ✓
- Hole range text ✓
- Logo (bottom-left) ✓
- QR code embedding — added to vinyl preview ✓
- Glass outline + clipping (warped mode) ✓

## Files Modified
| File | Changes |
|------|---------|
| `api/app/api/v1/render.py` | Glass mode now uses vinyl_preview rendering; computes terrain zones for glass mode |
| `api/app/services/render/svg.py` | Added dashed lines layer in vinyl preview; added QR code rendering to vinyl preview |
| `api/app/services/render/cricut.py` | Added dashed lines from hole numbers to tee boxes in white layer |

## Tests

### Updated Tests
- `test_render_glass_mode`: Now also checks for `beerGrad` (vinyl preview rendering)

### New Tests
- `test_dashed_lines_to_tee`: Verifies dashed line layer and stroke-dasharray
- `test_qr_code_in_vinyl_preview`: Verifies QR code embeds in vinyl mode

### Test Results
- **287 tests passed**, 0 failed, 0 errors
