# Task 013: Terrain-Following Scoring Zones (Rewrite) — DONE

## Summary
Rewrote scoring zone computation so zones follow actual course terrain (radiating outward from green, blending with fairway bounds) instead of horizontal bands. Added rendering in vinyl-preview, scoring-preview, and cricut-white modes.

## Changes

### 1. New Algorithm: `compute_terrain_following_zones()` (scoring.py)

**New dataclass `TerrainFollowingZone`:**
- `score`: int (-1 through +5)
- `polygon`: list of [x, y] points forming zone boundary
- `y_center`, `y_top`, `y_bottom`: vertical bounds
- `label_position`: {"x", "y", "inside"} for score label placement
- `leader_line`: optional [(x1,y1), (x2,y2)] dotted line for small zones

**Algorithm:**
1. Extracts green polygon from hole features (-1 zone = green itself)
2. Generates zones 0-5 as progressively larger offset polygons from green centroid
3. Zones +2 through +5 blend lateral bounds toward fairway edges (`_blend_polygon_with_fairway()`)
4. All zones clamped within `available_top` / `available_bottom` bounds
5. Label positions computed: inside centroid for large zones, outside with leader line for small zones

**New helper functions:**
- `_polygon_area()` — shoelace formula for area computation
- `_extract_fairway_polygons()` — get all fairway shapes from features
- `_fairway_width_at_y()` — find fairway lateral extent at a y-coordinate
- `_offset_polygon_uniform()` — uniform pixel-distance offset from centroid
- `_blend_polygon_with_fairway()` — blend polygon toward fairway bounds

**Old code removed:**
- `compute_terrain_zones()` and `compute_all_terrain_zones()` replaced
- `_TERRAIN_LERP`, `_lerp_contour_to_rect()`, `_clamp_contour_x()`, `_clamp_contour_y()`, `_offset_polygon()` removed

### 2. Rendering: `_render_terrain_zones()` (svg.py)

New function renders terrain zones in two modes:
- **Vinyl mode** (vinyl-preview/glass): white stroked polygon boundaries, white score labels, dotted leader lines
- **Scoring-preview mode**: colored filled polygons (green → yellow → orange → red gradient), black score labels

Wired into:
- `_render_vinyl_preview()` — renders terrain zones as white contour lines
- `render_svg()` main function — renders in scoring-preview mode behind features

### 3. Cricut White Layer (cricut.py)

- Replaced old scoring arcs (concentric circles) with terrain zone polygon contours
- `render_cricut_white()` now accepts optional `terrain_zones` parameter
- Renders zone boundary paths as cut lines and score numbers as cut text
- Skips -1 zone (green rendered as feature)

### 4. Render API (render.py)

- Updated import: `compute_all_terrain_following_zones` replaces `compute_all_terrain_zones`
- Terrain zones computed for vinyl-preview, scoring-preview, cricut-white, and cricut-all modes
- Serialization updated for new `TerrainFollowingZone` fields (polygon, label_position, leader_line)
- Terrain zones passed to cricut_white in both main render and dedicated cricut endpoint

## Files Modified
| File | Changes |
|------|---------|
| `api/app/services/render/scoring.py` | New `TerrainFollowingZone` dataclass, `compute_terrain_following_zones()`, `compute_all_terrain_following_zones()`, helper functions. Old terrain zone code removed. |
| `api/app/services/render/svg.py` | New `_render_terrain_zones()` function. Wired into vinyl-preview and scoring-preview. |
| `api/app/services/render/cricut.py` | `render_cricut_white()` accepts terrain_zones param. Old scoring arcs replaced with zone contours. |
| `api/app/api/v1/render.py` | Updated to use new terrain zone API. Terrain zones computed for more modes. |

## Tests

### Updated Tests (test_scoring.py)
- `TestComputeTerrainFollowingZones` (8 tests): triangular green, green matching, growth, clamping, fallback, fairway blending, labels, leader lines, dataclass
- `TestComputeAllTerrainFollowingZones` (2 tests): single hole, empty layout

### Updated Tests (test_svg_renderer.py)
- `test_terrain_zone_contours_rendered`: verifies zones render in vinyl mode
- `test_terrain_zone_labels_rendered`: verifies score labels appear
- `test_terrain_zone_leader_lines`: verifies dotted leader lines for small zones

### Test Results
- **285 tests passed**, 0 failed, 0 errors
