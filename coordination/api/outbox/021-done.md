# Task 021: Increase Hole Spacing + Fix Stats Box Positioning — DONE

## Summary
Increased minimum hole spacing from 4px to 28px, added green-to-tee gap enforcement (30px min), and fixed stats box positioning to always be on the outer side of the tee away from the fairway.

## Part 1: More Space Between Holes

### layout.py
- `_fix_overlaps()`: `min_gap` changed from 4 to **28**
- `_pack_holes()`: `target_gap` changed from 4 to **28**
- New `_enforce_green_tee_gap()` function added:
  - For each consecutive pair of holes, finds lowest Y of upper hole's green features and highest Y of lower hole's tee features
  - If gap < 30px, pushes lower hole down to create 30px gap
  - Runs after `_fix_overlaps()` and before `_rescale_to_fill()`
  - Ensures adequate space for below-green scoring zones

### scoring.py
- Verified `MIN_ZONE_HEIGHT = 8` and `_merge_small_zones()` already present from Task 018

## Part 2: Fix Stats Box Positioning

### svg.py — `_render_hole_stats()`
- **Positioning logic rewritten**: Stats now placed based on tee-to-green direction:
  - If `start_x < end_x` (tee on left): stats go LEFT of hole number (toward left margin)
  - If `start_x > end_x` (tee on right): stats go RIGHT of hole number (toward right margin)
  - Stats always on the **outer** side of tee, away from fairway
- **Size reduced**: Box width 30px → **24px**
- **Font sizes adjusted**: 4.5px (rect mode), 3.5px (glass mode) — was 5/4px
- **Padding reduced**: padding_x 4→3, padding_y 2.5→2

## Files Modified
| File | Changes |
|------|---------|
| `api/app/services/render/layout.py` | `min_gap`/`target_gap` 4→28; new `_enforce_green_tee_gap()` (30px min) |
| `api/app/services/render/svg.py` | Stats box positioning based on tee-green direction; box 24px; font 3.5/4.5px |

## Tests
- **298 tests passed**, 0 failed, 0 errors
