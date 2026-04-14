# Task 016: Fix Cricut Export + Remove Remaining Terrain Zone Artifacts

**Priority**: Critical — exports still broken
**Depends on**: Nothing (Phase A)

---

## Part 1: Fix Cricut Export Multi-Glass Response

### Problem
When `glass_count > 1`, the API returns `{"glasses": [{white, green, ...}, ...]}` but the frontend expects `{white, green, tan, blue, guide}` directly. This causes empty/corrupt downloads.

### Required Fix in `render.py`
- Verify the `/render/cricut` endpoint response structure
- For multi-glass: ensure the response shape is consistent and documented
- Add try/catch with detailed error responses around the render pipeline
- Verify all render functions (`render_cricut_white`, `render_cricut_green`, `render_cricut_tan`, `render_cricut_blue`) return non-empty SVG strings
- If any layer fails, return a 500 with a descriptive error message (not empty SVGs)

### Validation
- Test the `/api/v1/render/cricut` endpoint with a sample course payload with 1 glass and 3 glasses
- Verify response contains valid SVG in all layer fields

## Part 2: Remove Remaining Terrain Zone Artifacts

### Problem
Stray horizontal lines from terrain zone contour rendering are still visible in some modes.

### Required Fix in `svg.py`
- Search for ANY remaining code that renders terrain zone contours as closed `<path>` elements with white strokes
- Specifically in `_render_vinyl_preview()`: if there's still a block iterating `terrain_zones` and drawing white stroke paths, remove it
- The proper terrain-following zones from Task 013 (`_render_terrain_zones()`) should be the ONLY zone rendering
- Verify `_render_scoring_arcs()` is fully removed (should be from Task 011, but confirm)

## Files to Modify
| File | Changes |
|------|---------|
| `api/app/api/v1/render.py` | Add try/catch, verify response structure, detailed error messages |
| `api/app/services/render/svg.py` | Remove any remaining terrain zone artifact rendering |

## Definition of Done
1. `/render/cricut` returns valid SVGs for 1-glass and multi-glass configurations
2. No stray horizontal lines in any rendering mode
3. All existing tests pass + new tests for multi-glass cricut response
