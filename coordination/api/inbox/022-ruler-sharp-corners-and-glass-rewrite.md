# Task 022: Ruler Sharp Corners + Glass Ruler Rewrite (Phase C)

**Priority**: High
**Depends on**: Task 021 (layout stable)

**IMPORTANT**: The glass ruler has been reported broken multiple times. This MUST be visually verified before delivery. Render a real course in glass mode and confirm the ruler is legible.

---

## Part 1: Sharp Corners on Ruler Rectangles (Issue 1)

### Changes in `svg.py` — `_render_ruler()` (rect mode)
- Remove ALL `rx` attributes from ruler score rectangles
- Score rectangles should span the **full width between the dual-side tick marks**
  - Rectangle left edge = left tick endpoint
  - Rectangle right edge = right tick endpoint
  - Tick marks become the edges of the rectangle (not separate elements)
- Hole number rectangles: also remove `rx` — sharp corners

## Part 2: Complete Rewrite of Glass Ruler (Issue 5)

### Problem
The warped ruler is a mangled white mess — overlapping shapes, unreadable text.

### Rewrite `_render_ruler_warped()` from scratch

**Design — match rect ruler in polar space:**

1. **Spine line**: Radial line along the right edge of the sector (at `edge_angle`)
2. **Hole number column** (inward from spine):
   - Trapezoidal cells (wider at outer radius, narrower at inner)
   - Odd holes: white fill, dark text
   - Even holes: white outline, white text
   - Numbers rotated to read along the radial direction
3. **Score label column** (outward from spine or overlapping ticks):
   - Sharp-cornered trapezoids spanning each zone's angular extent
   - Odd scores: white fill, dark text
   - Even scores + -1: white outline, white text
4. **Dual-side tick marks**: Radial lines extending inward AND outward from spine at zone boundaries
5. **Zone bands**: Alternating subtle opacity bands (same as rect)

**Space reservation:**
- In `glass_template.py`: increase right-side reserve to **12%** (from current 9%)
- If 12% isn't enough for clean rendering, go to **15%**

**Scaling:**
- Font sizes proportional to glass sector size
- Minimum font: 3px — below this, skip the label
- Test at default glass dimensions (146mm H, 43mm top R, 30mm bottom R)

**Anti-overlap:**
- After computing all label positions in polar space, check for overlap
- If two labels would overlap: hide the one from the smaller zone
- Never render overlapping text

### Polar Coordinate Helpers
The existing warp functions in `glass_template.py` convert (x, y) to polar. For the ruler:
- Y position maps to angle along the sector arc
- X position maps to radius (inner = bottom of glass, outer = top)
- "Left" in ruler terms = more inward (smaller radius)
- "Right" = more outward (larger radius)

## Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Remove `rx` from rect ruler rects; widen to span ticks; complete rewrite of `_render_ruler_warped()` |
| `api/app/services/render/glass_template.py` | Increase right-side reserve to 12-15% |

## Definition of Done
1. Rect ruler: sharp-cornered rectangles spanning full tick width
2. Glass ruler: legible, clean design matching rect ruler language
3. Glass ruler: hole numbers on inner side, scores on outer side, no overlap
4. Glass ruler: dual-side radial tick marks at zone boundaries
5. Glass ruler doesn't overlap with hole content (adequate reserved space)
6. No overlapping text anywhere on the ruler
7. Visually verified in BOTH rect and glass modes with a real course
8. All tests pass
