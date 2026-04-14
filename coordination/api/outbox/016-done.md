# Task 016: Fix Cricut Export + Remove Remaining Terrain Zone Artifacts — DONE

## Summary
Added error handling and SVG validation to the cricut endpoint, verified multi-glass response structure, and confirmed all old terrain zone artifacts are fully removed.

## Part 1: Fix Cricut Export

### Error Handling (render.py)
- Wrapped the entire cricut render loop in try/catch with detailed error messages
- Each layer is validated after rendering: must be a non-empty string containing `<svg`
- If any layer fails validation: returns 500 with `"Cricut layer '{name}' produced empty or invalid SVG (glass {i})"`
- If an unexpected exception occurs: returns 500 with `"Failed to render cricut layers for glass {i}: {error}"`
- HTTPException (validation errors) re-raised as-is

### Response Structure
- **Single glass** (`glass_count=1`): returns `{white, green, tan, blue, guide}` directly
- **Multi-glass** (`glass_count>1`): returns `{"glasses": [{white, green, tan, blue, guide}, ...]}`
- Verified both structures with new tests

## Part 2: Remove Remaining Terrain Zone Artifacts

### Verified Clean
- `_render_scoring_arcs()` — fully removed (confirmed: no references in svg.py)
- Old terrain contour loop — fully removed from `_render_vinyl_preview()` (replaced by `_render_terrain_zones()` in Task 013)
- `_render_terrain_zones()` (the new Task 013 function) is the only zone renderer
- The `tz.get("contour", [])` fallback in `_render_terrain_zones()` is a harmless compatibility path that handles both old dict format and new polygon format

### No Artifacts
- No code renders terrain zones as white-stroked closed paths outside of `_render_terrain_zones()`
- `scoring_arcs` removed from `ALL_LAYERS` (Task 011)
- No bulls-eye concentric circles remain

## Files Modified
| File | Changes |
|------|---------|
| `api/app/api/v1/render.py` | Added try/catch around cricut render loop, SVG validation for all layers, descriptive error messages |

## Tests

### New Tests (TestCricutMultiGlass)
- `test_single_glass_response_shape`: Verifies flat response with all 5 layer keys, no "glasses" wrapper
- `test_multi_glass_response_shape`: Verifies "glasses" array with 2 entries, each with all 5 layer keys containing valid SVG
- `test_multi_glass_all_layers_non_empty`: Verifies all layers have substantial content (>50 chars)

### Test Results
- **292 tests passed**, 0 failed, 0 errors
