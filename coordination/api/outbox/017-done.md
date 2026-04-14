# Task 017: Reserve Ruler Space + Stats Box Layout Padding — DONE

## Summary
Added ruler margin and stats margin to the layout engine, increased glass template reserves, so ruler and stats boxes don't overlap hole content.

## Part 1: Reserve Ruler Space

### layout.py
- Added `ruler_margin` parameter (default 65px) — reduces `draw_right` by this amount
- `draw_right = canvas_width - margin_x - ruler_margin` (was `canvas_width - margin_x`)
- Ensures hole content never extends into the ruler zone on the right edge

### glass_template.py
- Right-side reserve increased from `0.02` (2%) to `0.09` (9%) in `warp_pt()` normalization
- This pushes all warped content left, leaving ~9% of the sector width for the ruler
- Calculation: `nx = text_reserve + ((x - min_x) / content_w) * (1 - text_reserve - 0.09)`

### svg.py
- Warped ruler already renders at `edge_angle = half_a` (sector edge), which is outside the content area
- No changes needed — the increased reserve provides sufficient space

## Part 2: Stats Box Layout Padding

### layout.py
- Added `stats_margin` parameter (default 25px) — added to `draw_left`
- `draw_left = text_margin + stats_margin` (was `text_margin`)
- Provides 25px extra on the left for stats boxes and course name

### glass_template.py
- Left `text_reserve` increased from `0.06` (6%) to `0.08` (8%)
- Provides more room for stats boxes and course name text in glass mode

## Files Modified
| File | Changes |
|------|---------|
| `api/app/services/render/layout.py` | Added `ruler_margin` (65px) reducing `draw_right`; added `stats_margin` (25px) increasing `draw_left` |
| `api/app/services/render/glass_template.py` | Right reserve 2% → 9%; left text_reserve 6% → 8% |

## Tests

### New Tests
- `test_draw_area_includes_ruler_margin`: Verifies draw_right = 900 - 30 - 65 = 805, draw_left = 60 + 25 = 85
- `test_custom_ruler_margin`: Verifies custom ruler_margin parameter works

### Test Results
- **294 tests passed**, 0 failed, 0 errors
