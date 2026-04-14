# Task 010: Ruler Readability Overhaul

## Priority: HIGH
## Depends on: 009 (vinyl preview SVG — ruler extended to glass mode)
## Phase: Post-Phase 5 enhancement

## Summary
Rewrite `_render_ruler()` in svg.py to fix readability issues: text too small, labels overlapping, no zone range indicators, no hole boundary dividers, compressed below-green zones unreadable.

## File to Modify
`api/app/services/render/svg.py` — rewrite `_render_ruler()` function

## Requirements

### 1. Increase all text sizes
- Score labels: **8pt minimum** (currently 4pt)
- Hole number labels: **12pt minimum** (currently 8pt)
- Tick line stroke width: **1px** (currently 0.5px)
- Ruler spine stroke width: **1px** (currently 0.5px)

### 2. Alternate labels left and right of ruler spine
Stagger score labels on alternating sides to prevent vertical overlap:
- **Even-index zones** (e.g., +5, +3, +1): label and tick on the **LEFT** side of the ruler
- **Odd-index zones** (e.g., +4, +2, 0): label and tick on the **RIGHT** side of the ruler
- This doubles effective vertical spacing between adjacent labels

### 3. Show zone range extent
Each zone should have a visible range indicator:
- Draw a **thin vertical bracket** (or highlighted segment along ruler spine) spanning the zone's full y_top to y_bottom
- Use **alternating opacity** to distinguish adjacent zones (e.g., alternating 5% opacity white background bands)
- The bracket connects top tick and bottom tick of each zone

### 4. Clear hole boundary indicators
Add prominent visual separators between holes:
- **Horizontal rule** spanning full ruler width at each hole boundary
- **Thicker stroke** (2px) vs zone ticks (1px)
- **Hole number** in a small **pill/badge** shape: rounded rect with stroke, bold text centered inside
- Slight extra vertical gap at hole boundaries if possible

### 5. Handle compressed below-green zones
The +1/+2 zones below the green are often extremely narrow. When zones are too small:
- **Minimum label spacing**: if two labels would be closer than 10px vertically, offset them horizontally or use a **leader line** (small angled line from label to tick)
- **Combine labels**: show "+1/+2" as a single combined label if both zones are < 8px tall
- **Below-green specifically**: place labels slightly outside zone boundaries with small arrows/lines pointing in

### 6. Both modes
All improvements must work in:
- **Rect mode**: straightforward vertical layout
- **Glass/warped mode**: ruler along right edge of annulus sector (from Task 009)

For glass mode, the same principles apply but with scaled-down sizes appropriate for the warped geometry. Minimum text sizes may need adjustment (e.g., 5pt minimum instead of 8pt) to fit the curved space.

## Visual Target
```
  ┌─────────────────────────┐
  │         +5          ─── │ ← label left, tick left
  │  ─── +4                 │ ← label right, tick right
  │         +3          ─── │
  │  ─── +2                 │
  │         +1          ─── │
  │  ───  0                 │
  │     [ -1 GREEN ]    ─── │ ← green zone highlighted
  │  ─── +1                 │ ← below-green zone
  │         +2          ─── │
  ├═════════════════════════┤ ← thick hole boundary
  │        ┌───┐            │
  │        │ 9 │            │ ← bold hole number badge
  │        └───┘            │
  ├═════════════════════════┤
  │         +5          ─── │
  │  ...                    │
  └─────────────────────────┘
```

## Tests
- Test that score labels have font-size >= 8 (parse SVG text elements)
- Test that labels alternate sides (check x-coordinates alternate between two values)
- Test that hole boundaries have thicker strokes than zone ticks
- Test that hole number badges exist (rounded rect + text)
- Test label collision handling: create zones < 8px tall and verify combined labels
- Test both rect and glass mode output
- All existing tests still pass

## Definition of Done
- [ ] All ruler text legible at 100% zoom (8pt+ score labels, 12pt+ hole numbers)
- [ ] Labels alternate left/right — no overlapping
- [ ] Zone range brackets or bands visible
- [ ] Hole boundaries have bold dividers + hole number badges
- [ ] Below-green compressed zones readable (combined labels or leader lines)
- [ ] Works in both rect and glass/warped modes
- [ ] All existing tests pass
- [ ] New ruler readability tests pass
