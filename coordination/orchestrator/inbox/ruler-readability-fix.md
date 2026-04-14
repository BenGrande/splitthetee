# Ruler Readability Overhaul

## Problem

The ruler on the right side of the rectangular SVG export is unreadable. Screenshots show:

1. **Text is far too small** — score labels are 4pt, hole numbers 8pt. Even zoomed in, they're hard to read. On a physical glass these would be microscopic.
2. **Labels overlap** — the below-green zones (+1, +2/+8) stack directly on top of each other because the vertical space is tiny. The zoomed screenshot clearly shows "+1" and "+8" overlapping into an illegible mess.
3. **All labels and ticks are on the same side** — every score label sits left of the ruler line with its tick extending left. When zones are narrow, consecutive labels pile up vertically.
4. **No hole boundary indicators** — there's no clear visual divider between where one hole ends and the next begins. The faint "H8", "H9" labels are the only hint, and they blend into the score labels.
5. **No sense of zone range** — each tick mark is a single line. There's no bracket, shading, or other visual cue showing the vertical extent each score covers.

## Required Changes

### 1. Increase all text sizes
- Score labels: **8pt minimum** (currently 4pt)
- Hole number labels: **12pt minimum** (currently 8pt)
- Tick line stroke width: **1px** (currently 0.5px)
- Ruler spine stroke width: **1px** (currently 0.5px)

### 2. Alternate labels left and right
Stagger score labels on alternating sides of the ruler spine to prevent vertical overlap:
- **Even-index zones** (e.g., +5, +3, +1): label and tick on the **left** side of the ruler
- **Odd-index zones** (e.g., +4, +2, 0): label and tick on the **right** side of the ruler
- This doubles the effective vertical spacing between adjacent labels

### 3. Show zone range extent
Each zone should have a visible bracket or range indicator:
- Draw a **thin vertical bracket** (or highlighted segment along the ruler spine) spanning the zone's full y_top to y_bottom
- Use **alternating opacity or slight indent** to distinguish adjacent zones
- The bracket connects the top tick and bottom tick of each zone, making the covered range obvious at a glance
- Consider alternating light background bands behind every other zone (very subtle, like 5% opacity white)

### 4. Clear hole boundary indicators
Add prominent visual separators between holes on the ruler:
- **Horizontal rule** spanning the full ruler width at each hole boundary
- **Thicker stroke** (2px) compared to zone ticks (1px)
- **Hole number** centered in a small **pill/badge** shape between the boundary lines, larger and bolder than current "H8" text
- Optional: slight extra vertical gap at hole boundaries

### 5. Handle compressed below-green zones
The +1/+2 zones below the green are often extremely narrow. When zones are too small to fit a label:
- **Minimum label spacing**: if two labels would be closer than 10px vertically, offset them horizontally or use a **leader line** (small angled line from the label to the tick position)
- **Combine labels** when zones are tiny: show "+1/+2" as a single combined label if both zones are < 8px tall
- For the below-green section specifically: consider placing labels slightly outside the zone boundaries with arrows pointing in

## Files to Modify

| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Rewrite `_render_ruler()` — increase sizes, alternate sides, add zone brackets, add hole dividers, handle label collision |

## Visual Reference

Current (broken):
```
     +5 ─┤   ← all labels same side, tiny 4pt text
     +4 ─┤
     +3 ─┤   ← labels overlap when zones are narrow
     +2 ─┤
     +1 ─┤
      0 ─┤
     -1 ─┤
  +1+8 ─┤   ← overlap! unreadable
   H8     ← faint, blends in
     +5 ─┤
     ...
```

Target:
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

## Acceptance Criteria

1. All ruler text is legible at 100% zoom in the designer preview
2. No label overlapping — adjacent labels never touch or stack
3. Each zone's vertical range is visually obvious (bracket or band)
4. Hole boundaries are immediately clear with bold dividers + hole number badges
5. Below-green compressed zones remain readable (combined labels or leader lines)
6. Works in both rect and glass/warped modes

## Priority

**High** — The ruler is the dispute-resolution mechanism for the game. If players can't read it, the product doesn't work.
