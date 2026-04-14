# Task 011: Fix Export Endpoints + Remove Terrain Zone Artifacts (Phase A)

**Priority**: Critical — unblocks all other work
**Depends on**: Nothing
**Supersedes**: Parts of 008, 009

---

## Part 1: Verify Export Endpoints

The frontend export flow calls these API endpoints. Ensure they return valid content:

### 1A. `/api/v1/render` (POST) — Single SVG render
- Verify the endpoint returns valid SVG with correct `Content-Type: image/svg+xml` or JSON with SVG string
- Verify the response body is not empty when given valid course data
- Add proper error responses (400/422) when input is invalid
- Test with a real course payload

### 1B. `/api/v1/render/cricut` (POST) — Cricut layers
- Verify endpoint returns JSON with `white`, `green`, `tan` SVG strings
- Verify none of the layer SVGs are empty
- Verify CORS headers allow the frontend origin
- Add error handling for missing/invalid course data

### Files to Check/Modify
| File | Changes |
|------|---------|
| `api/app/api/v1/render.py` | Verify render and cricut endpoints; add error handling; ensure valid SVG returned; check Content-Type headers |

---

## Part 2: Remove Terrain Zone Contour Artifacts from Vinyl Preview

The terrain zone contours in `_render_vinyl_preview()` produce visual artifacts (stray horizontal lines). Remove this rendering until the new terrain-following zone system is implemented in Task 013.

### What to Remove
In `svg.py`, the `_render_vinyl_preview()` function has a section that renders terrain zone contours as closed paths:
```python
if terrain_zones:
    for hole_tzs in terrain_zones:
        for tz in hole_tzs:
            contour = tz.get("contour", [])
            d = _coords_to_path(contour, closed=True)
            svg += f'<path d="{d}" fill="none" stroke="#ffffff" stroke-width="0.5" opacity="0.3"/>'
```

**Remove or comment out this entire block.** Replace with a simple comment: `# Terrain-following zone contours will be added in a future task`

Also remove the `_render_scoring_arcs()` bulls-eye concentric circle rendering — this will be replaced by the new terrain-following zone system.

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Remove terrain zone contour rendering from vinyl preview; remove `_render_scoring_arcs()` function (or comment out) |

---

## Definition of Done
1. `/api/v1/render` returns valid, non-empty SVG for a test course payload
2. `/api/v1/render/cricut` returns valid JSON with non-empty `white`, `green`, `tan` SVG strings
3. Proper error responses for invalid input (not 500 errors)
4. Vinyl preview mode produces clean output with no stray horizontal lines
5. Bulls-eye concentric circles removed
6. All existing tests pass (update/remove tests that assert on removed features)
7. New tests for export endpoint validation
