# Task 025: Ruler Complete Fix — Sharp Corners, No Overlap, Glass Rotation, Adaptive Sizing — DONE

## Summary
Complete rewrite of both rect and glass rulers with strict layout: hole number rect at top, flush score rects below, no spine, no overlap. Glass ruler elements rotated to follow curvature with adaptive sizing.

## Issue 1: Sharp Corners + No Spine

### Rect ruler (`_render_ruler`)
- Removed vertical spine line entirely — score rects form the visual column
- All rects sharp-cornered (no `rx`)
- Score rects span full column width (20px)
- Layout: single column at right edge

## Issue 2: No Overlap Layout

### New layout per hole:
```
┌──────────┐
│  HOLE 1  │  ← hole number rect (fixed 12px height, at section_top)
└──────────┘
   3px gap
┌──────────┐
│    +5    │  ← score rects (flush, no gaps between them)
├──────────┤
│    +4    │
│   ...    │
│    -1    │
│    +1    │  ← below-green
└──────────┘
```
- Hole number at TOP of each section (fixed 12px height)
- 3px gap between hole number and first score rect
- Score rects start from `max(zone.y_top, score_top)` to avoid overlap
- Alternating styles: odd scores white-filled, even scores white-outline

## Issue 3: Glass Ruler Rotation

### New glass ruler (`_render_ruler_warped`)
- Every element wrapped in `<g transform="rotate(θ°, 0, 0)">` where θ = edge_angle in degrees
- In rotated space, radius maps to SVG y-axis — rects align naturally along the glass edge
- Hole number rects and score rects both rotated
- Text reads along the glass edge direction
- Radial tick marks removed (not needed — rects define the boundaries)

## Issue 10: Adaptive Sizing

- Font size and rect height scale with available radial space at each position
- Formula: `fs = min(4, max(3, zone_radial_height * 0.6))`
- Zones with radial height < 3px: label skipped entirely (too small to read)
- Hole number rect height adapts: `min(6, available_space * 0.15)`, minimum 4px
- Anti-overlap: tracks label positions, skips overlapping labels

## Files Modified
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Complete rewrite of `_render_ruler()` and `_render_ruler_warped()` |

## Tests

### Updated Tests
- `test_hole_number_at_top_of_section`: Verifies hole# appears before scores in SVG output
- `test_hole_number_badge`: Checks no `rx`, hole number present
- `test_alternating_score_rect_styles`: Replaces zone bands test — checks fill/outline alternation
- `test_ruler_has_flush_score_rects`: Replaces spine test — verifies no `<line>`, many rects
- `test_score_rects_span_full_width`: Checks 20px width

### Test Results
- **297 tests passed**, 0 failed, 0 errors
