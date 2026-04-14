# Task 011: Fix Export Endpoints + Remove Terrain Zone Artifacts — DONE

## Summary
Fixed export endpoints with input validation and removed terrain zone visual artifacts from vinyl preview and scoring arcs from standard render.

## Part 1: Export Endpoint Validation

### `/api/v1/render` (POST)
- Added input validation: returns 422 for missing `holes` field or non-array `holes`
- Endpoint already returned valid SVG with correct structure; verified non-empty responses for valid course data
- Error responses are now proper 422 (validation) instead of 500 (server error)

### `/api/v1/render/cricut` (POST)
- Added input validation: 422 for missing/non-array `holes`, 400 for empty `holes` array
- Verified endpoint returns JSON with `white`, `green`, `tan`, `guide` SVG strings (all non-empty)
- CORS already configured in `app/main.py` with `allow_methods=["*"]` and `allow_headers=["*"]`

### Files Modified
| File | Changes |
|------|---------|
| `api/app/api/v1/render.py` | Added `HTTPException` import; added input validation to both `/render` and `/render/cricut` endpoints |

## Part 2: Remove Terrain Zone Contour Artifacts

### Terrain Zone Contours
- Removed the entire terrain zone contour rendering block from `_render_vinyl_preview()` in `svg.py`
- The block rendered white-stroked closed paths that produced stray horizontal line artifacts
- Replaced with comment: `# Terrain-following zone contours will be added in a future task`

### Scoring Arcs (Bulls-eye Concentric Circles)
- Removed `_render_scoring_arcs()` function entirely from `svg.py`
- Removed the scoring arcs rendering call from the main `render_svg()` function
- Removed `"scoring_arcs"` from `ALL_LAYERS` list

### Files Modified
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Removed terrain zone contour block from `_render_vinyl_preview()`; removed `_render_scoring_arcs()` function; removed scoring arcs layer from `render_svg()`; removed from `ALL_LAYERS` |

## Tests

### Updated Tests
- `test_scoring_arcs_with_zones` -> `test_scoring_arcs_removed`: now asserts scoring arcs layer is absent
- `test_terrain_zone_contours` -> `test_terrain_zone_contours_removed`: now asserts terrain zones layer is absent

### New Tests (in `TestRenderValidation`)
- `test_render_missing_holes`: verifies 422 when holes field missing
- `test_render_holes_not_array`: verifies 422 when holes is not an array
- `test_render_valid_returns_svg`: verifies valid SVG returned for valid input
- `test_cricut_missing_holes`: verifies 422 when holes field missing
- `test_cricut_empty_holes`: verifies 400 when holes array is empty
- `test_cricut_returns_all_layers`: verifies all 4 layers present and non-empty

### Test Results
- **278 tests passed**, 0 failed, 0 errors
