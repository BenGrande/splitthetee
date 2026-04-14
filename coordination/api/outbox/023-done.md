# Task 023: Score Numbers on Course + Fix Cricut Export — DONE

## Summary
Verified and improved score number rendering in vinyl preview, fixed cricut white layer to include ruler in warped mode, and added course_name/hole_range pass-through to cricut pipeline.

## Part 1: Score Numbers on Course

### svg.py — `_render_terrain_zones()`
- **Already rendering**: Function was already rendering score labels at `label_position` with leader lines — verified working
- **Improved visibility**: Increased opacity from 0.7 to 0.8 in vinyl mode
- **Font size**: 4px vinyl mode, 5px scoring-preview mode
- **Leader lines**: opacity increased from 0.5 to 0.6 for better visibility
- Labels render at `label_position.x/y` when `inside == True`
- Labels render outside with dotted leader line when `inside == False`

## Part 2: Fix Cricut Export

### A. Ruler in warped cricut mode (cricut.py)
- Removed `not is_warped` guard on ruler rendering
- Added warped ruler implementation using polar coordinates:
  - Spine line along right edge of sector
  - Dual-side radial ticks at zone boundaries
  - Score labels positioned outward from spine
- Rect mode ruler preserved as `elif` branch

### B. course_name pass-through (render.py)
- Added `course_name` extraction from top-level data in cricut endpoint (same pattern as main render)
- `render_cricut_white()` already renders course_name via its opts dict

### C. hole_range computation and rendering
- **render.py**: Auto-computes `hole_range` as `"Holes {min}-{max}"` from hole refs if not provided
- **cricut.py**: Added hole_range rendering below course name (vertical rotated text in rect mode)

### D. All print elements verified in white cricut layer
- Feature outlines ✓
- Scoring zone boundary lines ✓ (via terrain_zones param)
- Score numbers ✓ (via terrain_zones labels)
- Hole number circles + dashed lines to tees ✓
- Hole stats boxes ✓
- Ruler (both rect AND warped modes) ✓
- Course name ✓
- Hole range text ✓
- Logo ✓ (via opts.logo_data_url)
- Scale ruler ✓

## Files Modified
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Improved score label opacity/font in terrain zones |
| `api/app/services/render/cricut.py` | Added warped ruler; added hole_range rendering |
| `api/app/api/v1/render.py` | Added course_name extraction and hole_range auto-computation in cricut endpoint |

## Tests
- **298 tests passed**, 0 failed, 0 errors
