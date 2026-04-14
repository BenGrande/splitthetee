# Task 021: Increase Hole Spacing + Fix Stats Box Positioning (Phase B)

**Priority**: High
**Depends on**: Task 020

**IMPORTANT**: After changes, render a real course and verify no elements overlap. Test BOTH rect and glass modes.

---

## Part 1: More Space Between Holes (Issue 2)

### Problem
Below-green zones are too compressed. `min_gap` and `target_gap` are only 4px.

### Changes in `layout.py`

**A. Increase gaps:**
- `_fix_overlaps()`: Change `min_gap` from 4 to **28**
- `_pack_holes()`: Change `target_gap` from 4 to **28**

**B. Add green-to-tee distance enforcement:**
After `_fix_overlaps()`, add a pass that:
1. For each consecutive pair of holes, find the lowest Y of the upper hole's green features and the highest Y of the lower hole's tee features
2. If distance < 30px, push the lower hole down to create 30px gap
3. This ensures scoring zones between holes have adequate height

### Changes in `scoring.py`
- Verify `MIN_ZONE_HEIGHT = 8` exists and `_merge_small_zones()` is called (from Task 018)
- If not present, add them

## Part 2: Fix Stats Box Positioning (Issue 3)

### Problem
Stats boxes overlap the fairway. They should be on the OUTER side of the tee, toward the canvas margin.

### How Zigzag Layout Works
- Odd-indexed holes: LEFT to RIGHT (tee on left, green on right)
- Even-indexed holes: RIGHT to LEFT (tee on right, green on left)

### Required Positioning in `svg.py` — `_render_hole_stats()`

**Holes going left-to-right (tee on left):**
- Stats box to the **LEFT** of hole number (toward left canvas margin, AWAY from fairway)
- Layout: `[stats sign] ← (hole#) ← [tee] ---- fairway ---- [green]`

**Holes going right-to-left (tee on right):**
- Stats box to the **RIGHT** of hole number (toward right canvas margin, AWAY from fairway)
- Layout: `[green] ---- fairway ---- [tee] → (hole#) → [stats sign]`

### Sizing
- Reduce box width to **24px** (was 30px)
- Font size: **3.5px** (glass mode), **4.5px** (rect mode)
- Keep stacked format (Par / yd / HCP)

### Determining Direction
The direction can be determined from the hole's tee and green positions:
- If tee_x < green_x (tee on left): stats go LEFT of hole number
- If tee_x > green_x (tee on right): stats go RIGHT of hole number
- Key: stats always go on the tee side, further OUT from the fairway

## Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/layout.py` | Increase `min_gap`/`target_gap` to 28; add green-to-tee distance enforcement |
| `api/app/services/render/svg.py` | Fix stats positioning: always on outer side of tee; reduce box to 24px; font 3.5/4.5px |

## Definition of Done
1. Minimum 28px gap between holes in layout
2. Below-green zones have visible height (no "+1/+2" combined labels)
3. Stats boxes never overlap fairway — always on outer side of tee toward canvas margin
4. Stats boxes sized appropriately (24px wide, 3.5-4.5px font)
5. Visually verified in both rect and glass modes
6. All tests pass
