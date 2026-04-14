# Task 024: Unify Glass Preview and Cricut Export Rendering — DONE

## Summary
Unified the glass preview and cricut export rendering pipelines by adding a `layer` parameter to `_render_vinyl_preview()`. All cricut layers now call through to the same rendering code as the glass preview, eliminating the export/preview mismatch.

## Architecture Change

### Before
- `_render_vinyl_preview()` in svg.py: rendered the glass preview
- `render_cricut_white/green/tan/blue()` in cricut.py: completely independent rendering pipeline
- Result: exports diverged from preview (different stats formats, missing elements, different styling)

### After
- `_render_vinyl_preview(layout, opts, layer="all")` in svg.py: single source of truth
- `render_cricut_white/green/tan/blue()` in cricut.py: thin wrappers that call `_render_vinyl_preview(layer=...)`
- Result: exports are guaranteed identical to preview elements

## Implementation

### svg.py — `_render_vinyl_preview()` layer parameter
- Added `layer` parameter: `"all"` (default), `"white"`, `"green"`, `"blue"`, `"tan"`
- Layer flags computed at top: `_all`, `_white`, `_green`, `_blue`, `_tan`
- **Background**: only when `layer == "all"`
- **Terrain zone contours**: when `_white` (white stroked boundaries)
- **Feature routing by layer**:
  - White cats (rough/path/boundary): when `_white`
  - Green fill (fairway): when `_green`
  - Green stroke (green/tee): when `_green`
  - Blue fill (water): when `_blue`
  - Tan fill (bunker): when `_tan`
- **White-only elements** (hole numbers, dashed lines, stats, ruler, course name, logo, QR): when `_white`
- Glass clip group always opens/closes for warped mode regardless of layer

### cricut.py — Thin wrappers
```python
def render_cricut_white(layout, zones_by_hole, template, opts, terrain_zones):
    return _render_vinyl_preview(layout, opts_with_zones, layer="white")

def render_cricut_green(layout, opts):
    return _render_vinyl_preview(layout, opts, layer="green")

def render_cricut_blue(layout, opts):
    return _render_vinyl_preview(layout, opts, layer="blue")

def render_cricut_tan(layout, opts):
    return _render_vinyl_preview(layout, opts, layer="tan")
```
- Old independent rendering code removed (~260 lines)
- `render_cricut_guide()` kept as-is (separate reference overlay)
- Helper functions (`_extract_features_by_category`, `_compact_arrange`, `_scale_ruler_element`, etc.) kept for potential future use

## What This Guarantees
1. Stats boxes in export = exact same stacked rounded-rect design as preview
2. Ruler in export = exact same sharp-cornered design as preview
3. Zone boundaries in export = same stroke widths and opacity as preview
4. Hole numbers, dashed lines, course name = identical
5. Any future preview improvement automatically appears in exports

## Files Modified
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Added `layer` parameter with gating throughout `_render_vinyl_preview()` |
| `api/app/services/render/cricut.py` | Rewrote white/green/blue/tan as thin wrappers calling shared renderer; removed ~260 lines of independent rendering code |

## Tests

### Updated Tests
- `test_basic_render` (cricut white): checks `#ffffff` instead of `stroke="white"`
- `test_includes_scale_ruler` → `test_includes_stats_boxes`: checks "Par 4"
- `test_warped_mode`: checks `glassClip` instead of `mm` units
- `test_includes_hole_stats`: checks "Par 4" / "400 yd" (was "P4" / "400y")
- `test_basic_render` (cricut green): checks `#4ade80` instead of `stroke="green"`
- Green/tan tests: updated for shared renderer output format (no reference labels, no mm units)
- `test_cricut_green_mode` (endpoint): checks `#4ade80`

### Test Results
- **297 tests passed**, 0 failed, 0 errors
