# Task 026: Layout Spacing, Stats Clipping, Course Name Padding, Thinner Outlines — DONE

## Summary
Reduced horizontal spread, increased glass template reserves, thinned outlines, added course name padding, and added boundary checking for stats boxes.

## Changes

### Issue 4: Reduce Horizontal Spread
- **layout.py**: `max_hole_width` reduced from 0.55 to **0.42** — narrower holes, more margin
- **glass_template.py**:
  - Content padding: 12px → **20px**
  - `edge_inset`: 3% → **5%**
  - Left `text_reserve`: 8% → **10%** (room for course name + stats)
  - Right reserve: 12% → **15%** (room for ruler + stats)

### Issue 5: Thinner Outlines
| Element | Before | After |
|---------|--------|-------|
| White features (rough/path/boundary) | 0.4 | **0.3** |
| Green outlines (green) | 0.6 | **0.4** |
| Tee outlines | 0.6 | **0.3** |
| Bunker fill stroke | 0.3 | **0.2** |
| Water/fairway fill strokes | 0.2 | 0.2 (unchanged) |

### Issue 6: Course Name More Padding
- `_build_text_paths()` offsets increased from `[0.01, 0.021, 0.031]` to **`[0.04, 0.055, 0.07]`**
- Course name text arc is 4% from left edge (was 1%)

### Issue 7: Stats Box Boundary Checking
- `_render_hole_stats()` now checks if box extends beyond canvas edges
- If `box_x < 0`: flips to other side of hole number
- If `box_x + box_w > canvas_width`: flips to other side
- Canvas width passed via `opts["_canvas_width"]`

## Files Modified
| File | Changes |
|------|---------|
| `api/app/services/render/layout.py` | `max_hole_width` 0.55 → 0.42 |
| `api/app/services/render/glass_template.py` | padding 12→20, edge_inset 3→5%, text_reserve 8→10%, right reserve 12→15% |
| `api/app/services/render/svg.py` | Reduced stroke widths; text arc offsets increased; stats box boundary flipping |

## Tests
- **297 tests passed**, 0 failed, 0 errors
