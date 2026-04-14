# Task 017: Reserve Ruler Space + Stats Box Layout Padding

**Priority**: High
**Depends on**: Task 016 (Phase B)

---

## Part 1: Reserve Ruler Space in Layout (Issue 5)

### Problem
The ruler in glass mode bleeds into the rightmost hole's content. No space is actually reserved for the ruler in the layout computation.

### Fix in `layout.py`
- Add a `ruler_margin` parameter to `compute_layout()` (default ~60-70px)
- Reduce `draw_right` by `ruler_margin`: `draw_right = canvas_width - margin_x - ruler_margin`
- This ensures hole content never extends into the ruler zone

### Fix in `glass_template.py`
- Increase right-side reserve in `warp_layout()` from 2% to **8-10%** of normalized width
- Change: `nx = text_reserve + ((x - min_x) / content_w) * (1 - text_reserve - 0.08)` (was `0.02`)
- This pushes all warped content left, leaving right edge for the ruler

### Fix in `svg.py`
- Adjust `_render_ruler_warped()` to render within the reserved right-edge space
- Ensure ruler ticks, labels, and hole number column fit the reserved zone

## Part 2: Stats Box Layout Padding (Issue 1 — padding only)

### Problem
Stats boxes on the first and last holes may extend beyond the canvas edge.

### Fix in `layout.py`
- Increase `text_margin` or add a `stats_margin` parameter (~25-30px extra on each side)
- Apply to both left and right edges so stats boxes have room

### Fix in `glass_template.py`
- Increase left `text_reserve` from 6% to ~8% to accommodate stats boxes + course name

## Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/layout.py` | Add `ruler_margin` (~60-70px) reducing `draw_right`; add `stats_margin` (~25-30px) on each side |
| `api/app/services/render/glass_template.py` | Right reserve 2% → 8-10%; left text_reserve 6% → 8% |
| `api/app/services/render/svg.py` | Adjust `_render_ruler_warped()` positioning to fit reserved space |

## Definition of Done
1. Ruler has its own reserved space — no overlap with hole content in glass mode
2. Stats boxes on edge holes don't overflow the canvas
3. Layout still looks balanced (not too much dead space)
4. All existing tests pass + updated layout tests
