# Task 019: Filled Fairway/Water with Knockouts + Ruler Score Rectangles — DONE

## Summary
Made fairway solid green fill and water solid blue fill in vinyl preview with SVG mask knockouts for score numbers. Ruler score labels now use alternating filled/outline rectangles.

## Part 1: Filled Blue Water & Filled Green Fairway

### svg.py — `_render_vinyl_preview()`
- **Fairway**: Moved from `_WHITE_CATS` (stroke-only) to new `_GREEN_FILL_CATS` set
  - Renders as `fill="#4ade80" stroke="#4ade80"` (solid green fill)
  - Rough, path, course_boundary remain as white stroke-only
- **Water**: Changed from `fill="none" stroke="#3b82f6"` to `fill="#3b82f6" stroke="#3b82f6"` (solid blue fill)

### Score Number Knockout
- Collects score label positions from terrain zones where `label_position.inside == True`
- For each filled fairway/water feature, creates an SVG `<mask>`:
  - Mask starts as white (fully visible)
  - Score number text drawn in black on mask (creating transparent holes)
  - Mask applied to the filled `<path>` element
- Score numbers appear as cutouts showing bare glass through colored vinyl

### cricut.py
- **Green layer** (`render_cricut_green`): Now includes fairway features as solid green fill alongside green/tee outlines
- **Blue layer** (`render_cricut_blue`): Water features now use solid blue fill instead of outline-only

## Part 2: Ruler Score Labels as Alternating Rectangles

### svg.py — `_render_ruler()` (rect mode)
- Score labels now render as rectangles spanning zone height, positioned right of spine
- **Odd scores** (+1, +3, +5): White-filled rectangle with dark knocked-out text (`fill="white"`, text `fill="#2a1f0e"`)
- **Even scores** (0, +2, +4) and -1: White-outline rectangle with white text inside
- Rectangles have `rx="2"` rounded corners
- Clear separation: hole numbers on LEFT column, score rectangles on RIGHT side

### svg.py — `_render_ruler_warped()` (glass mode)
- Same alternating pattern using circles instead of rectangles (works better in polar coordinates)
- Odd scores: white-filled circle with dark text
- Even scores: white-outline circle with white text
- All labels positioned outward from spine

## Files Modified
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Fairway filled green, water filled blue, SVG mask knockouts; ruler score labels as alternating rectangles/circles |
| `api/app/services/render/cricut.py` | Green layer includes filled fairway; blue layer uses solid fill |

## Tests

### Updated Tests
- `test_water_rendered_in_blue_fill`: Checks for `fill="#3b82f6"` (was stroke-only check)
- `test_fairway_rendered_as_filled_green`: New — checks for `fill="#4ade80"`
- `test_score_labels_in_rectangles`: Replaced alternating-sides test — checks for both fill styles and middle-anchored text

### Test Results
- **298 tests passed**, 0 failed, 0 errors
