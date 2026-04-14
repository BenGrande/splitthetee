# Task 013: Terrain-Following Scoring Zones (Rewrite)

**Priority**: High
**Depends on**: Task 011 (artifacts removed), Task 012 (blue vinyl)

---

## Overview
Rewrite the scoring zone computation so zones follow the actual course terrain (radiating outward from the green along the fairway) instead of being simple horizontal bands.

## Current State
- `scoring.py` has `compute_scoring_zones()` (horizontal y-bands) and `compute_terrain_zones()` (produces degenerate polygon artifacts)
- The old `compute_terrain_zones()` should be replaced entirely

## New Algorithm: `compute_terrain_following_zones()`

For each hole:

### Input
- Green polygon(s) from hole features
- Fairway polygon(s) from hole features
- Tee box position
- Hole bounding box
- Next hole's tee Y position (zone boundary limit)

### Zone Computation

1. **Extract green polygon** — the actual green feature shape
2. **Compute routing line** — path from tee box centroid to green centroid
3. **Generate zone boundaries as offset contours:**

| Zone | Score | How to compute |
|------|-------|---------------|
| Green interior | -1 (small greens) or -1 near hole + 0 outer (large greens) | The green polygon itself |
| Zone 0 | 0 | Offset green polygon outward by ~2-3px |
| Zone +1 | +1 | Offset further (~5-8px), still follows green shape |
| Zone +2 | +2 | Blend between green contour offset and fairway-bounded band. Use fairway width at this distance from green. |
| Zone +3 | +3 | Mostly follows fairway bounds. Band along routing line. |
| Zone +4 | +4 | Follows fairway bounds. Wider band. |
| Zone +5 | +5 | Widest band, extends to near tee box area |

4. **Zone width ratios**: Zones get wider further from green (more forgiveness for worse scores). Suggested ratios of remaining hole height: +1: 5%, +2: 10%, +3: 15%, +4: 25%, +5: 35%, with 0 and -1 taking ~10% combined.

5. **Fairway blending**: For zones +2 through +5:
   - Compute the fairway polygon's width at the zone's Y-position
   - Use the fairway edges as the lateral bounds of the zone
   - Where there's no fairway data, fall back to a gentle widening from the green shape

6. **Clamp**: No zone extends past `next_hole_y` (the next hole's tee area)

### Output: `TerrainFollowingZone` dataclass
```python
@dataclass
class TerrainFollowingZone:
    score: int           # -1, 0, 1, 2, 3, 4, 5
    polygon: list        # list of (x, y) points forming the zone boundary polygon
    y_center: float      # vertical center of zone (for ruler alignment)
    y_top: float         # top edge
    y_bottom: float      # bottom edge
    label_position: dict  # {"x": float, "y": float, "inside": bool} — where to put the score label
    leader_line: list | None  # [(x1,y1), (x2,y2)] if label is outside the zone
```

### Score Number Labels
For each zone, compute a label position:
- If zone polygon area is large enough (>100 sq px): place label **inside** the zone at centroid
- If zone is too small: place label **outside** the zone with a dotted **leader line** from label to zone

## Rendering Functions (in `svg.py`)

### `_render_terrain_zones(holes_data, terrain_zones, opts)`
New function to render the terrain-following zones:

**For vinyl-preview / glass mode:**
- Draw each zone boundary polygon as a white stroked path (no fill)
- Draw score number at `label_position` in white, ~4-5px font
- Draw dotted leader lines where `leader_line` is not None
- Style: `stroke="#ffffff" stroke-width="0.5" fill="none"`

**For scoring-preview mode:**
- Draw each zone polygon with semi-transparent colored fill
- Color gradient: green (-1) → yellow (0) → orange (+1/+2) → red (+3/+4/+5)
- Score labels in black for contrast

**For cricut-white layer:**
- Zone boundary paths as cut lines
- Score numbers as cut text

### Remove Old Zone Rendering
- Remove `_render_scoring_arcs()` (bulls-eye circles) if not already removed in Task 011
- Remove calls to old `compute_terrain_zones()`
- Keep `compute_scoring_zones()` (simple y-bands) as an internal fallback only

## Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/scoring.py` | Add `compute_terrain_following_zones()` returning `TerrainFollowingZone` list per hole. Remove old `compute_terrain_zones()`. |
| `api/app/services/render/svg.py` | Add `_render_terrain_zones()`. Remove `_render_scoring_arcs()`. Wire into vinyl-preview, scoring-preview, and standard modes. |
| `api/app/services/render/cricut.py` | Update white layer to include zone boundary contours and score labels |
| `api/app/api/v1/render.py` | Ensure terrain zones computed and passed to renderer for all relevant modes |

## Definition of Done
1. `compute_terrain_following_zones()` returns polygon-based zones that follow green and fairway shapes
2. Zones rendered as white contour lines in vinyl-preview / glass mode
3. Zones rendered as colored fills in scoring-preview mode
4. Score numbers visible in/near each zone with leader lines for small zones
5. No stray lines or visual artifacts
6. Zone contours included in cricut white layer
7. Old bulls-eye circles and degenerate terrain contours fully removed
8. All existing tests pass (update tests as needed) + comprehensive new tests
