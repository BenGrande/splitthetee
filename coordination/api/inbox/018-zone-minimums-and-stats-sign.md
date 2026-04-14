# Task 018: Zone Minimum Heights + Stats Sign Rendering

**Priority**: High
**Depends on**: Task 017 (layout padding in place)

---

## Part 1: Minimum Height for Below-Green Score Zones (Issue 2)

### Problem
Below-green zones (+1, +2) can become tiny slivers, producing confusing "+1/+2" combined labels.

### Fix in `scoring.py`
- Add `MIN_ZONE_HEIGHT = 8` constant (pixels)
- In `compute_scoring_zones()`: after computing below-green zone heights:
  - If +1 zone height < `MIN_ZONE_HEIGHT`: merge into +2 (absorb +1 into +2 — higher/worse score wins)
  - If both below-green zones combined < `MIN_ZONE_HEIGHT`: make one single +2 zone
  - Apply same logic to above-green zones if any is < `MIN_ZONE_HEIGHT` (merge upward toward higher score)

### Fix in `svg.py`
- Remove the `below_combined` merge logic in `_render_ruler()` and `_render_ruler_warped()`
- After scoring.py merges, each zone has a single score — no need for "+1/+2" combined labels
- Remove the 8px threshold check that triggers combined labels

## Part 2: Hole Stats as Tee Box Sign (Issue 1)

### Problem
Hole stats are tiny inline text (3.5px, 0.5 opacity) — nearly invisible.

### New Rendering in `svg.py` — Rewrite `_render_hole_stats()`

**Visual design — rounded rectangle sign:**
```
┌─────────┐
│  Par 4   │
│  356 yd  │
│  HCP 9   │
└─────────┘
```
- Rounded white-outline rectangle (`rx="2"`, `stroke="#ffffff"`, `fill="none"`)
- Each stat on its own line inside
- White text, font-size ~5-6px (rect mode) / ~4px (glass mode)
- Opacity: 0.8

**Positioning:**
- Placed on the **opposite side** of the hole number circle from the tee box
- Adjacent to the hole number circle
- Layout: `[tee box] ---- dashed line ---- (hole#) [stats sign]`
- For holes on the left side: stats to the right of hole number
- For holes on the right side: stats to the left of hole number

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/scoring.py` | Add `MIN_ZONE_HEIGHT`; merge below-green zones when too small (higher score wins) |
| `api/app/services/render/svg.py` | Remove "+1/+2" combined label logic from ruler; rewrite `_render_hole_stats()` as rounded rectangle sign with stacked stats |

## Definition of Done
1. No "+1/+2" combined labels on ruler — zones pre-merged in scoring computation
2. Below-green zones either have adequate height or merge to higher score
3. Stats sign renders as a rounded white-outline rectangle with Par/yardage/HCP on separate lines
4. Stats sign positioned next to hole number circle, opposite side from tee
5. Stats clearly legible (5-6px font, 0.8 opacity)
6. All existing tests pass + new tests for zone merging and stats rendering
