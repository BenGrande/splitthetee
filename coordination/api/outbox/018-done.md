# Task 018: Zone Minimum Heights + Stats Sign Rendering — DONE

## Summary
Added minimum zone height merging in scoring computation and rewrote hole stats as rounded rectangle signs.

## Part 1: Minimum Height for Below-Green Score Zones

### scoring.py
- Added `MIN_ZONE_HEIGHT = 8` constant
- Added `_merge_small_zones()` function called after zone computation:
  - **Below-green**: If +1 zone < 8px, merges into +2 (higher/worse score wins). If both combined < 8px, makes one +2 zone.
  - **Above-green**: Small zones merge upward toward higher score neighbor.
- `compute_scoring_zones()` now calls `_merge_small_zones()` before returning

### svg.py — Ruler cleanup
- Removed `below_combined` logic from both `_render_ruler()` and `_render_ruler_warped()`
- Removed `combine_threshold` variable from both rulers
- No more "+1/+2" combined labels — zones are pre-merged in scoring computation

## Part 2: Hole Stats as Tee Box Sign

### svg.py — Rewritten `_render_hole_stats()`
- **Old**: Tiny inline text (3.5px, 0.5 opacity) with dot-separated stats
- **New**: Rounded white-outline rectangle sign with stacked lines:
  ```
  ┌─────────┐
  │  Par 4   │
  │  356 yd  │
  │  HCP 9   │
  └─────────┘
  ```
- Rectangle: `rx="2"`, white stroke, no fill, 0.8 opacity
- Text: 5px font (rect) / 4px (warped), white, 0.8 opacity
- Each stat on its own line inside the box
- Positioned adjacent to hole number circle, on opposite side from tee box

## Files Modified
| File | Changes |
|------|---------|
| `api/app/services/render/scoring.py` | Added `MIN_ZONE_HEIGHT`, `_merge_small_zones()`, auto-merge in `compute_scoring_zones()` |
| `api/app/services/render/svg.py` | Removed combined label logic from both rulers; rewrote `_render_hole_stats()` as rounded rectangle sign |

## Tests

### New Tests (test_scoring.py)
- `test_small_below_zones_merged`: Verifies zones < 8px merge (higher score wins)
- `test_adequate_below_zones_not_merged`: Verifies adequate zones are kept separate
- `test_scoring_zones_auto_merge`: Verifies compute_scoring_zones auto-merges

### Updated Tests (test_svg_renderer.py)
- `test_no_combined_labels_zones_premerged`: Replaced old combined label test — verifies no "+1/+2" in output
- `test_stats_sign_rounded_rect`: Verifies stats render as rounded rect with "Par 4"

### Test Results
- **298 tests passed**, 0 failed, 0 errors
