# Task 008: Terrain-Following Scoring Zones — DONE

## Completed

### `compute_terrain_zones()` in `api/app/services/render/scoring.py`
- Added `TerrainZone` dataclass with `score`, `contour`, `y_center`, `y_top`, `y_bottom` fields
- Implements concentric offset contours around the green polygon:
  - **-1 zone**: exact green polygon
  - **0 zone**: small offset outward from green centroid
  - **+1 zone**: further offset along routing direction
  - **+2 through +5**: progressively larger offsets with lerp toward horizontal rectangles (30%/50%/70%/90%)
- Routing direction computed from green centroid toward tee
- Polygon offset elongated along routing direction (1.3x factor)
- X-coordinates clamped within hole bbox; Y-coordinates clamped above `next_hole_y`

### `compute_all_terrain_zones()` in `api/app/services/render/scoring.py`
- Computes terrain zones for all holes in a layout
- Determines hole bboxes and next-hole boundaries automatically

### Edge cases handled
- No green feature: falls back to ellipse in lower third of hole bbox
- Green polygon < 3 points: generates 8-point circle at centroid
- All contour points clamped within horizontal bounds
- Zones don't bleed past next_hole_y boundary

### `render.py` updates
- `vinyl-preview` accepted as a valid mode
- Both `vinyl-preview` and `scoring-preview` modes compute terrain zones
- Terrain zones serialized as `terrain_zones` field in render response
- `vinyl-preview` mode activates scoring preview rendering in SVG

### Backward compatibility
- Existing `compute_scoring_zones()` completely unchanged
- All 242 pre-existing tests still pass

### New tests (9 tests in `tests/test_scoring.py`)
- `test_triangular_green` — 7 zones returned with correct scores
- `test_minus1_matches_green` — -1 zone contour equals green polygon
- `test_plus5_nearly_horizontal` — +5 zone has valid contour with >= 3 points
- `test_zones_dont_exceed_next_hole_y` — all contour points respect boundary
- `test_fallback_no_green` — zones generated even without green feature
- `test_with_multiple_features` — realistic hole with fairway, bunker, green, tee
- `test_terrain_zone_dataclass_fields` — TerrainZone fields verified
- `test_single_hole` (AllTerrainZones) — layout-level computation
- `test_empty_layout` (AllTerrainZones) — empty input returns empty

## Test Results
251 tests passed, 0 failed.
