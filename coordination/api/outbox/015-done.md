# Task 015: Ruler Readability Overhaul V2 — DONE

## Summary
Rewrote both rect and warped rulers with dual-side tick marks, alternating filled/outline hole number rectangles on the left column, and rotated hole numbers.

## Changes

### A. Dual-Side Tick Marks (Both Modes)
- Every zone boundary tick now extends on **both sides** of the ruler spine
- Tick length: 8px (rect), 6px (warped) on each side
- Combined below-green zone ticks also dual-sided

### B. Hole Number Column (Left Side)
**Rect mode:**
- Vertical column of rectangles to the left of the ruler spine
- Each rectangle spans the hole's full zone section height
- **Odd holes** (1, 3, 5...): White filled rectangle, number in dark (`#2a1f0e`) — knocked out effect
- **Even holes** (2, 4, 6...): White outline rectangle (stroke only), number in white
- Numbers rotated 90 degrees (`rotate(-90)`) for sideways display

**Warped mode:**
- Same alternating filled/outline pattern
- Positioned inward from the spine along the sector edge
- Badge sized at 10x12px with `rx="2"` rounded corners

### C. Score Labels
- 8pt minimum font in rect mode (preserved from Task 010)
- Alternating left/right label stagger (preserved)
- Zone range bands with alternating opacity (preserved)

### D. Compressed Zone Handling
- Combined labels for below-green zones < 8px tall (preserved)
- Dual-side ticks for combined labels too

### E. Cricut White Layer Ruler
- Updated to match new design: spine line, dual-side ticks, score labels
- Tick length 5px on each side

## Files Modified
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Rewrote `_render_ruler()` and `_render_ruler_warped()` with dual-side ticks, hole number left column, rotated numbers, alternating fill/outline |
| `api/app/services/render/cricut.py` | Updated ruler to use spine + dual-side ticks |

## Tests

### Updated Tests
- `test_hole_number_badge`: Now checks for `rx="3"` and `rotate(-90)`
- `test_ruler_glass_mode`: Updated for `rx="2"` in warped mode

### New Tests
- `test_dual_side_ticks`: Verifies all horizontal tick marks span both sides of spine
- `test_hole_number_alternating_fill`: Verifies odd holes have white fill with dark text

### Test Results
- **289 tests passed**, 0 failed, 0 errors
