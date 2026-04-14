# Task 027: Hole Range Text + Score Zone Boundaries/Numbers on Course — DONE

## Summary
Fixed hole_range auto-computation in main render endpoint, verified warped text rendering, and added horizontal zone boundary lines for better visibility.

## Issue 8: "Holes X-Y" Text Under Course Name

### Warped rendering — already working
- `_render_warped_text()` renders `hole_range` along `textArc2` with `startOffset="50%"`
- `textArc2` positioned at offset 0.055 from left edge (updated in Task 026)
- Font: 4px white, 0.6 opacity

### Pipeline fix (render.py)
- Main render endpoint now auto-computes `hole_range` from hole refs (was only in cricut endpoint)
- `"Holes {min}-{max}"` computed if not provided in options
- Flows through to both glass preview and cricut exports via unified rendering

## Issue 9: Scoring Zone Boundaries + Score Numbers

### Terrain zone rendering — verified working
- `_render_terrain_zones()` renders zone boundary polygons as white strokes (0.3px, 0.3 opacity)
- Score labels render at `label_position` (4px white, 0.8 opacity)
- Leader lines render for small zones (dotted, 0.6 opacity)
- Function is called in vinyl preview mode when `terrain_zones` data is present

### New: Simple horizontal zone boundary lines
- Added `layer-zone_lines` group in vinyl preview
- For each hole, draws thin white horizontal lines at each zone `y_top`
- Lines span the hole's full horizontal extent (min to max x of all features ± 5px)
- Style: `stroke="#ffffff" stroke-width="0.2" opacity="0.25"`
- These provide clear visible zone markers even when terrain zone polygons are small
- Only rendered in white layer (`_white` flag)

## Files Modified
| File | Changes |
|------|---------|
| `api/app/api/v1/render.py` | Added auto-computation of `hole_range` in main render endpoint |
| `api/app/services/render/svg.py` | Added `layer-zone_lines` horizontal boundary lines from zones_by_hole data |

## Tests
- **297 tests passed**, 0 failed, 0 errors
