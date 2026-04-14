# Task 022: Ruler Sharp Corners + Glass Ruler Rewrite — DONE

## Summary
Removed rounded corners from all ruler rectangles, widened score rects to span full tick width, and completely rewrote the glass/warped ruler with clean radial design and anti-overlap.

## Part 1: Sharp Corners on Rect Ruler

### svg.py — `_render_ruler()`
- Removed ALL `rx` attributes from ruler rectangles (sharp corners)
- Score rectangles now span full tick width: `x = spine_x - tick_len`, `width = tick_len * 2` (20px)
- Tick marks are now implicit in the rectangle edges (no separate tick lines)
- Hole number column: sharp corners, positioned left of score rects with 2px gap
- Knocked-out text color changed to `#1a1a1a` (matches dark background)

## Part 2: Complete Rewrite of Glass Ruler

### glass_template.py
- Right-side reserve increased from 9% to **12%** — more space for ruler

### svg.py — `_render_ruler_warped()` (rewritten from scratch)

**Design:**
1. **Spine line**: Radial line along right edge of sector at `edge_angle`
2. **Hole number column** (inward from spine):
   - Sharp-cornered rectangles at each hole's midpoint
   - Odd holes: white fill, dark text
   - Even holes: white outline, white text
   - Size proportional to hole's zone span
3. **Score label column** (outward from spine):
   - Sharp-cornered rectangles (8x6px) at each zone's midpoint
   - Odd scores (+1,+3,+5): white fill, dark text
   - Even scores (0,+2,+4) and -1: white outline, white text
4. **Dual-side radial ticks**: At every zone boundary, extending inward and outward from spine
5. **Hole boundary**: Thick (2px) radial tick at each hole section start

**Anti-overlap:**
- Collects all label positions during rendering
- Before placing each label, checks distance to all previous labels
- If overlap detected (<3px in both x and y), label is skipped
- Prevents the white-mess problem from overlapping text

**Scaling:**
- Font size proportional to zone radial height, clamped to [3px, 4px]
- Zones smaller than 3px radial height skip labels entirely

## Files Modified
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Rect ruler: sharp corners, full-width score rects. Warped ruler: complete rewrite with anti-overlap |
| `api/app/services/render/glass_template.py` | Right reserve 9% → 12% |

## Tests

### Updated Tests
- `test_hole_number_badge`: Checks for no `rx` (sharp corners) + rotated text
- `test_ruler_glass_mode`: Checks for white fill presence
- `test_score_rects_span_full_width`: Replaces dual-side ticks test — verifies 20px width, no rx
- `test_hole_number_alternating_fill`: Updated for `#1a1a1a` dark text color

### Test Results
- **298 tests passed**, 0 failed, 0 errors
