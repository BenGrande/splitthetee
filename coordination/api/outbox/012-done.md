# Task 012: Add Blue Vinyl Color for Water Hazards — DONE

## Summary
Added blue (`#3b82f6`) as a fourth vinyl color for water hazards across all rendering modes and Cricut export.

## Changes

### 1. SVG Renderer — Water in Blue
- **`svg.py`**: Moved `"water"` out of `_WHITE_CATS` into new `_BLUE_CATS` set in `_render_vinyl_preview()`
- Water features now render with `stroke="#3b82f6"` (blue) instead of `stroke="#ffffff"` (white)
- Standard rect/glass modes already had blue-ish water styling (`#5b9bd5`) via the style dict — unchanged
- Vinyl-preview mode now shows water in distinct blue

### 2. Cricut Export — New Blue Layer
- **`cricut.py`**: Added `render_cricut_blue()` function
  - Extracts all water hazard features from layout
  - Compact arrangement for efficient vinyl cutting (same pattern as green/tan)
  - Uses blue color `#3b82f6` for strokes
  - Labels pieces as "W{hole_ref}"
- Updated `render_cricut_guide()`:
  - Water features now highlighted as colored pieces (was background/dim)
  - Water color updated from `#4488cc` to `#3b82f6` for consistency
  - Water features now labeled with "W{ref}" prefix

### 3. Render API — Blue Layer Endpoints
- **`render.py`**:
  - Added `render_cricut_blue` import
  - Added `cricut-blue` mode handling in `/render` endpoint
  - Added `cricut-blue` to glass template warping modes
  - Updated `cricut-all` response to include `blue` key
  - Updated `/render/cricut` dedicated endpoint to include `blue` layer

## Files Modified
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Water moved from white to blue category in vinyl-preview |
| `api/app/services/render/cricut.py` | Added `render_cricut_blue()`; updated guide for water |
| `api/app/api/v1/render.py` | Added cricut-blue mode; updated cricut-all and /render/cricut |

## Tests

### New Tests
- `test_water_rendered_in_blue`: Verifies water features use `#3b82f6` in vinyl preview
- `test_water_not_white_in_vinyl`: Verifies water is not rendered as white stroke
- `test_cricut_blue_mode`: Verifies cricut-blue mode returns SVG with blue color
- Updated `test_cricut_all_mode`: Now checks for `blue` key
- Updated `test_cricut_dedicated_endpoint`: Now checks for `blue` key and SVG content
- Updated `test_cricut_returns_all_layers`: Now validates blue layer

### Test Results
- **281 tests passed**, 0 failed, 0 errors
