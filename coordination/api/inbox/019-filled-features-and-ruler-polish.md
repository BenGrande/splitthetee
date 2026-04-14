# Task 019: Filled Fairway/Water with Knockouts + Ruler Score Rectangles

**Priority**: High
**Depends on**: Task 018 (zone minimums resolved)

---

## Part 1: Filled Blue Water & Filled Green Fairway (Issue 3)

### Problem
In vinyl preview, water and fairway are stroke-only outlines. They should be solid fills with score numbers knocked out.

### Changes in `svg.py` — `_render_vinyl_preview()`

**Fairway:**
- Move `"fairway"` from `_WHITE_CATS` to a new `_GREEN_FILL_CATS` set
- Render as `fill="#4ade80" stroke="#4ade80"` (solid green fill)
- Keep rough, path, course_boundary as white stroke-only

**Water:**
- Change water rendering from `fill="none" stroke="#3b82f6"` to `fill="#3b82f6" stroke="#3b82f6"` (solid blue fill)

**Score Number Knockout:**
- Score zone numbers that fall inside fairway or water polygons must be knocked out (bare glass visible through number)
- Implementation: Use SVG `<mask>` element:
  1. Create a mask for each filled feature area
  2. Mask starts as white (fully visible)
  3. Score number text shapes are drawn in black on the mask (creating transparent holes)
  4. Apply mask to the filled feature `<path>`
- This makes the score numbers appear as cutouts in the colored vinyl

### Changes in `cricut.py`
- `render_cricut_green()`: Include filled fairway shapes with score number paths cut out (as internal cut lines)
- `render_cricut_blue()`: Include filled water shapes with score number paths cut out

## Part 2: Ruler Score Labels as Alternating Rectangles (Issue 4B-D)

### Problem
Score labels are plain text that overlaps with hole numbers.

### Changes in `svg.py` — `_render_ruler()` and `_render_ruler_warped()`

**Score label style — alternating white/transparent rectangles:**
- **Odd score values** (+1, +3, +5): White-filled rectangle with score text knocked out (dark/transparent text via mask)
- **Even score values** (0, +2, +4) and -1: White-outline rectangle (no fill) with white text inside
- Each rectangle spans the zone's vertical extent (y_top to y_bottom)
- Rectangles sit between the dual-side ticks, centered on the ruler spine

**Separation from hole numbers:**
- Hole number column: LEFT side of ruler (per Task 015)
- Score rectangles: RIGHT side, between the dual-side ticks
- Clear gap between the two columns

**Full vertical coverage:**
- Below-green zones render score labels all the way down to zone boundary
- Ruler covers the full vertical extent of each hole's scoring area

## Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Fairway filled green, water filled blue, score knockout via SVG masks; ruler scores as alternating rectangles |
| `api/app/services/render/cricut.py` | Filled fairway in green layer with knockout paths; filled water in blue layer with knockout paths |

## Definition of Done
1. Fairway renders as solid green fill in vinyl preview
2. Water renders as solid blue fill in vinyl preview
3. Score numbers inside fairway/water areas are knocked out (visible as bare glass)
4. Cricut green layer has filled fairway with score cutouts
5. Cricut blue layer has filled water with score cutouts
6. Ruler score labels use alternating white-filled/outline rectangles
7. Scores and hole numbers clearly separated (no overlap)
8. All existing tests pass + new tests
