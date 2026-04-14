# Task 023: Score Numbers on Course + Fix Cricut Export (Phase D)

**Priority**: High
**Depends on**: Task 022 (ruler fixed), Task 020 (print accuracy)

**IMPORTANT**: Visually verify exported cricut SVGs by opening them in a browser.

---

## Part 1: Score Numbers on Course (Issue 7)

### Problem
No score numbers are rendered on the actual holes in glass view. Each zone should show its score.

### Implementation in `svg.py`

**A. Label placement per zone:**
- `_render_terrain_zones()` already receives zones with `label_position` and `leader_line` fields
- If `label_position.inside == True`: render score number at that position
- If `label_position.inside == False`: render score number at the label position with a dotted leader line from the number to the zone

**B. Vinyl preview rendering:**
- Score numbers: white text, 3-4px font (glass mode), 5px (rect mode)
- Leader lines: `stroke="#ffffff" stroke-dasharray="1,1" stroke-width="0.3" opacity="0.6"`
- For numbers inside filled fairway (green): use SVG `<mask>` to knock out (from Task 019 pattern)
- For numbers inside filled water (blue): same knockout mask

**C. Verify `_render_terrain_zones()` actually renders labels:**
- Check if the function currently renders the score labels at `label_position`
- If it does but they're invisible (wrong coordinates, zero opacity, clipped), fix the issue
- If it doesn't render them at all, add the rendering

### Fallback
If terrain zone polygons don't provide usable label positions:
- For each zone, place the score number at the horizontal center of the hole's fairway at y_mid of the zone
- This is the simple fallback approach

## Part 2: Fix Cricut Export (Issue 9)

### A. Include ruler in warped cricut export
In `cricut.py` — `render_cricut_white()`:
- Remove the `not is_warped` guard on ruler rendering
- Call `_render_ruler_warped()` for warped mode (using the fixed version from Task 022)
- The ruler is white vinyl — it belongs in the white layer

### B. Ensure course_name flows through cricut pipeline
In `render.py` — cricut endpoint:
- Read `course_name` from the request body
- Pass it to `render_cricut_white()` in the opts dict
- Verify `render_cricut_white()` renders the course name as vertical text

### C. Include hole_range in cricut export
- Compute "Holes X-Y" and pass through to `render_cricut_white()`
- Render below course name

### D. Verify ALL print elements in white cricut layer
After fixing, verify the white layer SVG contains:
- Feature outlines (fairway, rough, path, boundary)
- Scoring zone boundary lines
- Score numbers
- Hole number circles + dashed lines to tees
- Hole stats boxes (rounded rect + text)
- Ruler (full design including warped mode)
- Course name (vertical, left edge)
- Hole range text
- Logo (bottom)
- QR code (bottom)

## Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Ensure score numbers render in vinyl preview and rect modes; knockouts for filled features |
| `api/app/services/render/cricut.py` | Remove warped ruler guard; ensure course_name/hole_range included; add score numbers to layers |
| `api/app/api/v1/render.py` | Pass course_name and hole_range through cricut pipeline |

## Definition of Done
1. Score numbers visible on the course in both rect and glass modes
2. Numbers inside filled features are knocked out (bare glass showing)
3. Small zones have numbers outside with dotted leader lines
4. Cricut white layer includes ruler in warped mode
5. Cricut white layer includes course name and hole range
6. All cricut SVGs are valid and render in browser
7. Exported files download successfully (non-empty)
8. Visually verified in both modes + cricut export opened in browser
9. All tests pass
