# Task 026: Layout Spacing, Stats Clipping, Course Name Padding, Thinner Outlines (Phase C)

**Priority**: High
**Depends on**: Task 025 (ruler fixed)

**IMPORTANT**: Visually verify no content is clipped in glass mode after changes.

---

## Issue 4: Reduce Horizontal Spread

### Changes in `layout.py`
- Reduce `max_hole_width` from current value (likely 0.55) to **0.42**
- This makes each hole narrower, leaving more margin

### Changes in `glass_template.py`
- Content padding: increase from 12px to **20px**
- `edge_inset`: increase from 3% to **5%**
- Left `text_reserve`: increase to **10%** (room for course name + left-side stats)
- Right reserve: increase to **15%** (room for ruler + right-side stats)

## Issue 5: Thinner Outlines

### Changes in `svg.py` vinyl preview stroke widths
| Element | Current | New |
|---------|---------|-----|
| White features (rough/path/boundary) | 0.4 | **0.3** |
| Green outlines | 0.6 | **0.4** |
| Water outlines (around fill) | 0.2 | **0.2** (keep) |
| Bunker outlines | — | **0.2** |
| Tee outlines | — | **0.3** |
| Fairway fill stroke | 0.2 | **0.2** (keep) |

Since Task 024 unified rendering, these changes automatically apply to cricut exports.

## Issue 6: Course Name More Padding on Left

### Changes in `svg.py`
- In `_build_text_paths()` or wherever the warped text arc offset is defined: increase from `0.01` to **0.04** (4% of sector angle from left edge)

## Issue 7: Stats Box Clipping for Edge Holes

### Changes in `svg.py` — `_render_hole_stats()`
Before rendering a stats box, check if it would extend beyond bounds:

**For rect mode:**
- Check if `box_x < 0` or `box_x + box_w > canvas_width`
- If clipped: flip to other side of hole number

**For glass/warped mode:**
- After computing warped position, check if stats box would be outside glass clip area
- First/last holes: bias stats box toward interior of glass
- Fallback: place on other side of hole number if outer side would be clipped

## Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/layout.py` | Reduce `max_hole_width` to 0.42 |
| `api/app/services/render/glass_template.py` | Increase padding to 20px, edge_inset to 5%, text_reserve to 10%, right reserve to 15% |
| `api/app/services/render/svg.py` | Reduce stroke widths; increase course name text arc offset to 0.04; add boundary checking for stats boxes |

## Definition of Done
1. No content clipped by glass edges (stats boxes, hole numbers all visible)
2. Course name has breathing room from left edge
3. White outlines are thin and clean
4. Holes are not cramped against glass boundaries
5. Visually verified in both rect and glass modes
6. All tests pass
