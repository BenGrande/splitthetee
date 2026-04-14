# Task 008: Terrain-Following Scoring Zones

## Priority: HIGH
## Depends on: 007 (complete)
## Phase: Post-Phase 5 enhancement

## Summary
Replace the current geometric scoring zone computation (simple y_top/y_bottom horizontal bands) with contour-based zones that follow the terrain of each hole's green shape.

## File to Modify
`api/app/services/render/scoring.py`

## Requirements

### New function: `compute_terrain_zones()`
Add this alongside the existing `compute_scoring_zones()` (keep that as fallback).

**Algorithm:**
1. For each hole, extract the green feature polygon(s) from the hole's features list (category == "green")
2. Compute the green centroid and bounding shape
3. Generate concentric offset contours for each scoring zone:
   - **-1 zone**: the green polygon itself (list of [x,y] points)
   - **0 zone**: offset the green polygon outward by a small amount (2-3px in layout coordinates)
   - **+1 zone**: offset further outward, blending toward nearby rough/fairway features if available
   - **+2 through +5**: progressively larger offsets that increasingly become horizontal bands
     - Use linear interpolation (lerp) between the terrain contour shape and a simple horizontal rectangle
     - +2 ≈ 70% contour / 30% horizontal, +3 ≈ 50/50, +4 ≈ 30/70, +5 ≈ 10/90
4. The vertical extent of each zone still narrows toward the green (preserve existing zone_ratios: 25%/20%/17%/15%/13%/10%)
5. Zones must NOT bleed past the next hole's tee box boundary

**Polygon offset approach (start simple):**
- Use elliptical offsets around the green centroid, elongated along the hole's routing direction
- The routing direction = angle from green centroid toward tee centroid (or toward the first feature in the hole)
- Each successive zone offset = previous offset + zone_height * direction_factor
- For the lerp toward horizontal: blend each contour point's Y toward the zone's horizontal Y-center, and X toward the hole's horizontal center

**Return format:**
```python
@dataclass
class TerrainZone:
    score: int          # -1, 0, 1, 2, 3, 4, 5
    contour: list       # list of [x, y] points forming the zone polygon outline
    y_center: float     # vertical center of the zone (for ruler tick alignment)
    y_top: float        # bounding box top (for backwards compat)
    y_bottom: float     # bounding box bottom

def compute_terrain_zones(
    hole_features: list,
    hole_bbox: dict,        # {x, y, width, height} of the hole in layout coords
    next_hole_y: float | None,  # y position of next hole's tee (zone boundary)
    zone_ratios: list | None = None,
) -> list[TerrainZone]:
```

### Edge cases
- If no green feature found for a hole: fall back to an ellipse centered in the lower third of the hole bbox
- If green polygon has < 3 points: treat as a circle at the centroid
- Ensure all contour points stay within the hole's horizontal bounds (clamp X)

### Integration point
- The render endpoint (`api/app/api/v1/render.py`) should call `compute_terrain_zones()` when the mode is `vinyl-preview` or `scoring-preview`, falling back to `compute_scoring_zones()` for other modes
- Add a `terrain_zones` field to the render response (alongside existing `scoring_zones`)

### Update render.py
In `api/app/api/v1/render.py`:
- Accept `vinyl-preview` as a valid mode value
- When mode is `vinyl-preview` or `scoring-preview`, compute terrain zones and include in response
- Pass terrain zones through to the SVG renderer

## Tests
- Test `compute_terrain_zones()` with a mock hole containing a triangular green
- Test that -1 zone matches the green polygon
- Test that +5 zone is nearly horizontal (lerp factor ~0.9)
- Test that zones don't exceed next_hole_y boundary
- Test fallback when no green feature exists
- Test with real-ish hole data (multiple features)

## Definition of Done
- [ ] `compute_terrain_zones()` exists in scoring.py and returns TerrainZone objects with polygon contours
- [ ] Zones lerp from terrain-following (-1) to horizontal (+5)
- [ ] render.py accepts `vinyl-preview` mode and computes terrain zones
- [ ] Existing `compute_scoring_zones()` unchanged (backward compat)
- [ ] All existing tests still pass
- [ ] New tests for terrain zones pass
