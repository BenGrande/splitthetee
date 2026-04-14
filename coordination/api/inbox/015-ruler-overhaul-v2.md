# Task 015: Ruler Readability Overhaul V2

**Priority**: High
**Depends on**: Task 013 (terrain zones — for accurate zone boundaries)

---

## Overview
Further improve the ruler based on new design requirements. This builds on the work in Task 010 but adds new layout features.

## Changes Required

### A. Tick Marks on BOTH Sides of Ruler Spine
Every zone boundary gets a tick mark extending **left AND right** of the vertical ruler line (currently ticks are only on one side or alternating). Both-side ticks make it unambiguous where each zone starts and ends.

### B. Hole Numbers Moved to LEFT Side of Ruler
Move hole numbers from inline with scores to a **vertical column of rectangles on the left edge of the ruler area**.

**Design:**
- Each hole gets a rectangular cell in a vertical column
- **Odd-numbered holes** (1, 3, 5...): White **filled** rectangle with the hole number **knocked out** (number is clear/bare glass — use clip-path or mask)
- **Even-numbered holes** (2, 4, 6...): White **outline** rectangle (stroke only, no fill) with the hole number in **white** text inside
- Hole numbers **rotated 90 degrees** (sideways) inside rectangles
- Alternating pattern provides easy visual scanning

### C. Score Labels
- Score labels (-1, 0, 1, 2, 3, 4, 5) next to tick marks
- 8pt minimum in rect mode
- Alternating left/right stagger to prevent overlap (keep from Task 010)
- Zone range visible via alternating subtle background bands (keep from Task 010)

### D. Zone Range Brackets
- Thin vertical bracket or highlighted spine segment spanning each zone's full extent
- Alternating opacity to distinguish adjacent zones (keep from Task 010)

### E. Compressed Zone Handling
- Combined labels for zones < 8px tall (keep from Task 010)
- Leader lines for labels that would overlap

## Visual Layout
```
 ┌──────┐  ─── +5 ──────  ← ticks on BOTH sides
 │  1   │  ─── +4 ──────
 │(side)│  ─── +3 ──────
 └──────┘  ─── +2 ──────
 ┌──────┐  ─── +1 ──────
 │      │  ─── 0  ──────
 │  2   │  ─── -1 ──────  (green zone)
 │      │  ─── +1 ──────  (below-green)
 └──────┘
```

Left column: alternating white-filled/outline rectangles with sideways hole numbers.
Right column: ruler spine with dual-side ticks and score labels.

## Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Rewrite `_render_ruler()` and `_render_ruler_warped()` — add dual-side ticks, move hole numbers to left column with alternating fill/outline rectangles, rotated numbers |
| `api/app/services/render/cricut.py` | Update ruler in white cricut layer to match new design |

## Definition of Done
1. Tick marks extend on BOTH sides of ruler spine at every zone boundary
2. Hole numbers in alternating white-filled/outline rectangles on the left side of ruler
3. Hole numbers rotated 90 degrees (sideways)
4. Odd holes: white fill + knocked-out number; Even holes: white outline + white number
5. Score labels remain legible with no overlapping
6. Works in both rect and glass/warped modes
7. Cricut white layer includes updated ruler design
8. All existing tests pass + updated ruler tests
