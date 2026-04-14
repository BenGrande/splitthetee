# Task 027: Hole Range Text + Score Zone Boundaries/Numbers on Course (Phase D)

**Priority**: High
**Depends on**: Task 026 (layout stable)

---

## Issue 8: "Holes X-Y" Text Under Course Name

### Problem
Hole range text not visible under course name in glass mode. In `cricut.py` the warped hole_range rendering is `pass` (skipped).

### Fix in `svg.py`
- Verify `hole_range` renders along `textArc2` in `_render_warped_text()`
- Check that `textArc2` is properly defined and positioned (should be slightly offset inward from the course name arc)
- Since Task 024 unified rendering, this fix carries to cricut exports automatically

### Fix in render pipeline
- Verify `hole_range` is computed and passed through from the render endpoint
- `render.py` already auto-computes `hole_range` from hole refs (added in Task 023) — verify this still works

## Issue 9: Scoring Zone Boundaries + Score Numbers on Course

### Problem
No zone boundary lines or score numbers visible on the actual course layout in glass view.

### What Should Exist
1. **Zone boundary lines**: Thin white lines at each zone boundary, crossing the fairway/hole width horizontally
2. **Score numbers**: Small white numbers inside each zone
   - Inside the zone if large enough
   - Outside with dotted leader line if too small
3. **Knockout**: Numbers inside filled fairway (green) or water (blue) should be knocked out

### Implementation
Check `_render_terrain_zones()` in `svg.py`:
- Is it being called in vinyl preview mode?
- Are zone boundary lines being rendered as white strokes?
- Are score labels being rendered at `label_position`?
- Are leader lines rendering for small zones?

If the function exists but output is invisible:
- Check coordinates — are labels at valid positions within the canvas?
- Check opacity — is it too low?
- Check if the terrain zones data is actually being passed to the function

If the function isn't producing useful zone boundaries:
- Add simple horizontal line rendering at each `y_top`/`y_bottom` boundary
- Lines should span the hole's horizontal width (from left edge to right edge of hole features)
- Score numbers centered in each zone band

### Fallback approach
If terrain zone polygons aren't producing good results, use the simple scoring zones (`compute_scoring_zones()` y-bands):
- Draw horizontal white lines at each zone boundary
- Place score numbers at the center of each zone band

## Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Verify/fix hole_range rendering; verify/fix zone boundaries and score numbers rendering |

## Definition of Done
1. "Holes X-Y" visible below course name in both rect and glass modes
2. Scoring zone boundaries visible as thin white lines on each hole
3. Score numbers visible inside or adjacent to each zone
4. Numbers knocked out where overlapping filled features
5. Visually verified in both modes
6. All tests pass
