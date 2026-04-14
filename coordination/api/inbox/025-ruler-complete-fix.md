# Task 025: Ruler Complete Fix — Sharp Corners, No Overlap, Glass Rotation, Adaptive Sizing (Phase B)

**Priority**: Critical
**Depends on**: Task 024 (unified rendering)

**IMPORTANT**: Visually verify the ruler in BOTH rect and glass modes before marking done. The glass ruler has been broken in every previous round.

---

## Issue 1: Sharp Corners + No Spine Behind Score Rects

### In `_render_ruler()` (rect mode):
- Remove ALL `rx` attributes from score label rectangles (sharp corners)
- Hole number rectangles CAN keep small rounded corners
- **Remove the vertical spine line** from behind the score area — score rectangles form the visual column. Spine only visible in gaps (if any) or removed entirely
- Score rectangles span the full width between dual-side tick endpoints

## Issue 2: Hole Numbers and Scores Must Not Overlap

Layout for each hole on the ruler:
```
┌──────────┐
│  HOLE 1  │  ← hole number rect (top of section, fixed height)
└──────────┘
┌──────────┐
│    +5    │  ← score rects (sharp corners, flush, no gaps)
├──────────┤
│    +4    │
├──────────┤
│   ...    │
├──────────┤
│    -1    │
├──────────┤
│    +1    │  ← below-green
└──────────┘
┌──────────┐
│  HOLE 2  │
└──────────┘
```

- Hole number rect at TOP of each hole's section, fixed height (~10-12px)
- Small gap (2-3px) between hole number rect and first score rect
- Score rects stack below, each spanning its zone's y_top to y_bottom
- Score rects flush against each other (no gaps)
- **No vertical overlap** between hole numbers and scores

## Issue 3: Glass Ruler — Elements Must Rotate With Curvature

### Problem
Ruler elements on glass are flat/horizontal rectangles placed at polar coordinates but NOT rotated to follow the glass curvature.

### Fix
Every ruler element at angle θ must be rotated by `θ * 180/π` degrees:

```python
angle_deg = math.degrees(theta)
# Wrap element in rotation transform:
f'<g transform="rotate({angle_deg}, {cx}, {cy})">'
```

- Rectangles: rotated to align tangentially with the glass arc
- Text: rotated to read along the glass edge
- Tick marks (radial lines): already correct — they extend inward/outward

Apply to ALL elements in `_render_ruler_warped()`.

Since Task 024 unified rendering, this fix will automatically apply to cricut exports too.

## Issue 10: Adaptive Sizing at Bottom of Glass

The glass sector narrows toward the bottom (inner radius). Ruler elements for lower holes get compressed.

### Fix
- Font size and rect height scale with available radial space at each position
- At smaller radius: elements are proportionally smaller
- Minimum readable font: 3px — below this, skip the label (render tick mark only)
- Consider: same angular slice is physically narrower at inner_r vs outer_r

## Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Rewrite `_render_ruler()` (sharp corners, no spine, no overlap layout) and `_render_ruler_warped()` (rotation transforms, adaptive sizing) |

## Definition of Done
1. Rect ruler: sharp-cornered score rects, no spine behind them, no overlap with hole numbers
2. Glass ruler: all elements rotated to follow glass curvature
3. Glass ruler: readable at bottom (adaptive sizing, skip unreadable labels)
4. Hole numbers at top of section, scores below, clear separation
5. Score rects flush against each other, spanning full tick width
6. Visually verified in BOTH rect and glass modes
7. All tests pass
