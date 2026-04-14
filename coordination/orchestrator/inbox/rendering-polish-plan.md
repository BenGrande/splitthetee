# Rendering Polish Plan — Stats Signs, Zone Minimums, Filled Features, Ruler Fix, Course Persistence

**Date**: 2026-04-13
**Priority**: High — these are the visual and functional issues visible in the current build

**Context**: Screenshots from 2026-04-13 8:30-8:31 PM show the rect and glass views. The rect view has a ruler with overlapping scores/hole numbers, weird horizontal lines (terrain zone artifacts), and no course title. The glass view has a mangled white ruler band bleeding into the rightmost hole, no course title, and small inline stats text.

---

## Issue 1: Hole Stats as Tee Box Sign

### Problem
Hole stats (Par, yardage, HCP) are rendered as tiny inline text (font-size 3.5, opacity 0.5) placed 15px from the tee. They're nearly invisible, especially in glass mode.

### Current Code
`api/app/services/render/svg.py` — `_render_hole_stats()` (line ~370):
- Single line: `"Par 4 · 356 yd · HCP 9"`
- Font-size: 3.5
- Opacity: 0.5
- Position: `start_x ± 15, start_y + 8`

### Required Changes

**Visual design — tee box sign:**
- Rounded white-outline rectangle (no fill, white stroke, rounded corners ~2px)
- Each stat on its own line inside the rectangle:
  ```
  ┌─────────┐
  │  Par 4   │
  │  356 yd  │
  │  HCP 9   │
  └─────────┘
  ```
- White text, font-size ~5-6px (rect mode) / ~4px (glass mode)
- Opacity: 0.8 (more visible than current 0.5)

**Positioning:**
- Placed on the **opposite side** of the hole number circle from the tee box
- Immediately adjacent to the hole number circle
- Layout: `[tee box] ---- (3) [stats sign]`
- The hole number circle sits between the tee and the stats box

**Layout padding for stats boxes:**
- The first hole (leftmost) and last hole (rightmost) may have stats boxes that extend beyond the current draw area
- Add additional **left padding** for the first hole's stats box and **right padding** for the last hole's stats box
- In `layout.py`: increase `text_margin` or add a `stats_margin` parameter (~25-30px extra on each side)
- In `glass_template.py`: increase the right-side reserve from 2% to ~5% in the warp function, and left text_reserve from 6% to ~8%

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Rewrite `_render_hole_stats()` — rounded rectangle with stacked text lines, repositioned next to hole number circle on opposite side from tee |
| `api/app/services/render/layout.py` | Add extra left/right padding to accommodate stats boxes that may extend beyond hole content |
| `api/app/services/render/glass_template.py` | Increase right-side reserve in warp function to accommodate stats boxes |

---

## Issue 2: Minimum Height for Below-Green Score Zones

### Problem
The below-green zones (+1, +2) are split 50/50 of whatever space remains between the green bottom and the next hole's tee. When this space is small, both zones become tiny slivers and get merged into a "+1/+2" combined label on the ruler. This is confusing — a combined zone should just use the **higher (worse) score**.

### Current Code
`api/app/services/render/scoring.py` — `compute_scoring_zones()` (line ~149):
- Below-green space divided exactly in half: `half = below_space / 2`
- No minimum height check
- Ruler merge in `svg.py` at threshold of 8px produces "+1/+2" label

### Required Changes

**Minimum zone height:**
- Define a `MIN_ZONE_HEIGHT` constant (e.g., 6-8px)
- If a below-green zone would be smaller than `MIN_ZONE_HEIGHT`, **merge it into the adjacent higher-score zone**
- Merge strategy: if +1 zone is too small, absorb it into +2 (the higher/worse score wins)
- If BOTH below-green zones are too small combined, merge everything into a single +2 zone
- Same logic applies to above-green zones if they're very compressed

**Ruler label:**
- Stop showing combined "+1/+2" labels — after merging, each zone has a single definitive score
- Remove the `below_combined` merge logic in `_render_ruler()` and `_render_ruler_warped()` since zones are already properly merged in the scoring computation

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/scoring.py` | Add `MIN_ZONE_HEIGHT` constant; merge below-green zones when too small (higher score wins); apply same logic to any compressed above-green zones |
| `api/app/services/render/svg.py` | Remove the "+1/+2" combined label logic in `_render_ruler()` and `_render_ruler_warped()` — zones are now pre-merged |

---

## Issue 3: Filled Blue Water & Filled Green Fairway with Knocked-Out Score Numbers

### Problem
In vinyl preview mode, water and fairway are rendered as stroke-only outlines. The user wants:
- **Water**: Filled blue (solid blue vinyl, not just outline)
- **Fairway**: Filled green (solid green vinyl, not just outline)
- **Score numbers** that fall inside these filled areas should be **knocked out** (cut out of the vinyl, showing bare glass through the number shape)

### Current Code
`api/app/services/render/svg.py` — `_render_vinyl_preview()` (line ~499):
- `_WHITE_CATS = {"fairway", "rough", "path", "course_boundary"}` → rendered as white stroke, no fill
- `_BLUE_CATS = {"water"}` → rendered as blue stroke, no fill

### Required Changes

**Fairway rendering (vinyl preview + cricut green layer):**
- Change from `fill="none" stroke="#ffffff"` to `fill="#4ade80" stroke="#4ade80"` (or appropriate green)
- Fairway is now a solid green filled shape
- Move fairway from `_WHITE_CATS` to a new `_GREEN_FILL_CATS` set

**Water rendering (vinyl preview + cricut blue layer):**
- Change from `fill="none" stroke="#3b82f6"` to `fill="#3b82f6" stroke="#3b82f6"` (solid blue)
- Water is now a solid blue filled shape

**Score number knockout:**
- When rendering score zone numbers (from Issue 4 of the previous plan — terrain-following zones), any number that falls inside a fairway or water polygon must be **knocked out**
- Implementation approach: Use SVG `<mask>` or `<clipPath>` to cut the number shapes out of the filled feature paths
- Alternative: Render features first, then render score numbers with `fill="none"` and use the feature fill as a mask where the text shape is subtracted
- For Cricut production: The cut file must show the number as a void in the colored vinyl — this means the number path is part of the cut path for that color layer

**Cricut layer updates:**
- `render_cricut_green()`: Fairway shapes are now filled cuts (not just outlines) with score numbers knocked out
- `render_cricut_blue()`: Water shapes are filled cuts with score numbers knocked out

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Change fairway to filled green, water to filled blue in vinyl preview; implement score number knockout via SVG masking |
| `api/app/services/render/cricut.py` | Update green layer to include filled fairway shapes with knocked-out numbers; update blue layer for filled water with knocked-out numbers |

---

## Issue 4: Ruler Score Display & Weird Lines Fix

### Problem (visible in rect screenshot)
1. Score labels on the ruler **overlap with hole numbers** — the alternating white/clear hole number rectangles and the score tick labels are competing for the same space
2. The "weird horizontal lines" from terrain zone contour rendering are still present
3. Scores should use the **same alternating white/transparent pattern** as hole numbers

### Current Code
- Ruler in `svg.py` `_render_ruler()` (line ~146): Hole number column at `spine_x - ruler_width/2 - 8`, score labels on alternating sides of spine
- Terrain zone contours rendered as white stroke paths in vinyl preview mode (line ~428)

### Required Changes

**A. Fix terrain zone horizontal lines:**
- Remove or disable the terrain zone contour rendering that produces artifact lines
- In `_render_vinyl_preview()`: remove the `if terrain_zones:` block that draws white stroke paths for each terrain zone contour
- These will be replaced by the proper terrain-following zone system (from the previous comprehensive plan)

**B. Ruler score labels — alternating white/transparent rectangles:**
- Same visual pattern as hole numbers:
  - **Odd score values** (1, 3, 5): White-filled rectangle with score knocked out (transparent text)
  - **Even score values** (0, 2, 4) and special (-1): White-outline rectangle with white score text inside
- Score rectangles sit **between the dual-side ticks**, centered on the ruler spine
- Each score rectangle spans the vertical extent of its zone (y_top to y_bottom)
- This replaces the current plain text labels

**C. Separate hole numbers from scores:**
- Hole number column is on the **left** side of the ruler (per the previous plan)
- Score rectangles are on the **right** side, between the ticks
- Clear visual separation — hole numbers and scores never overlap

**D. Scores should go low enough:**
- Ensure the below-green zones (+1, +2 or merged single zone from Issue 2) render score labels all the way down to the zone boundary
- The ruler should cover the **full vertical extent** of each hole's scoring area, not stop short

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Remove terrain zone artifact rendering; rewrite score labels as alternating white/transparent rectangles between dual ticks; ensure scores and hole numbers don't overlap; verify full vertical coverage |

---

## Issue 5: Glass Ruler Overlap with Rightmost Hole

### Problem (visible in glass screenshot)
The ruler in glass/warped mode is a thick white band that bleeds into the rightmost hole's content area. The ruler and course content are fighting for the same space on the right edge of the glass.

### Root Cause
- In `glass_template.py` `warp_layout()`: right-side reserve is only **2%** of normalized width (line ~177: `1 - text_reserve - 0.02`)
- In `layout.py`: right margin is only **30px** (`margin_x`)
- The ruler (50px wide) is drawn on top of content that extends to the right edge
- No space is actually reserved for the ruler in the layout computation

### Required Changes

**A. Reserve ruler space in layout computation:**
- In `layout.py`: Add a `ruler_margin` parameter (default ~60-70px) that reduces `draw_right`
- `draw_right = canvas_width - margin_x - ruler_margin` → holes are positioned to leave room for the ruler
- This ensures no hole content extends into the ruler zone

**B. Reserve ruler space in glass warp:**
- In `glass_template.py`: Increase right-side reserve from 2% to **8-10%** of normalized width
- `nx = text_reserve + ((x - min_x) / content_w) * (1 - text_reserve - 0.08)` (was 0.02)
- This pushes all warped content left, leaving the right edge for the ruler

**C. Ruler rendering in glass mode:**
- In `_render_ruler_warped()`: Position ruler elements in the reserved right-edge space
- Ensure ruler ticks, labels, and hole number column fit within the reserved zone
- Reduce ruler width if needed to fit the glass curvature

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/layout.py` | Add `ruler_margin` parameter to `compute_layout()` reducing draw_right |
| `api/app/services/render/glass_template.py` | Increase right-side reserve in warp function from 2% to 8-10% |
| `api/app/services/render/svg.py` | Adjust `_render_ruler_warped()` to render within the reserved space |

---

## Issue 6: Course Title and "Holes X-Y" Missing / Not Persisting

### Problem
The course name and "Holes X-Y" text disappear on page reload because the course data is stored only in Pinia (in-memory). The text shows up after a fresh search but vanishes on refresh.

### Root Cause
- `frontend/src/stores/course.ts`: Course data is in-memory only (Pinia store resets on reload)
- `frontend/src/views/DesignerView.vue` (line ~86): On mount, it reads `route.query.lat`, `route.query.lng`, `route.query.courseId` and re-fetches course data — but only if those params exist in the URL
- When a user searches and selects a course, the URL is NOT updated with the course params
- On reload: no URL params → no course data fetched → no course name → no title rendered

### Required Changes

**A. Persist course selection in URL:**
- When a course is selected (after search + selection + hole data loaded), update the URL with query params:
  ```
  /designer?lat=XX.XXX&lng=YY.YYY&courseId=ZZZZ
  ```
- Use `router.replace()` (not `router.push()`) to avoid polluting browser history
- This way, on reload, `onMounted` reads the params and re-fetches course data

**B. Pass course_name and hole_range to renderer:**
- Verify that `buildRenderOptions()` in `designer.ts` includes `course_name` and `hole_range` in the options sent to the render API
- `course_name`: from `courseStore.courseData.courseName`
- `hole_range`: computed from the holes assigned to the current glass (e.g., "Holes 1-6")

**C. Verify backend renders title:**
- In `svg.py`: `_render_rect_text()` and `_render_warped_text()` already render course name and hole range when passed in opts
- Ensure the opts actually contain these values through the full render pipeline

### Files to Modify
| File | Changes |
|------|---------|
| `frontend/src/views/DesignerView.vue` | After course selection, update URL with `router.replace({ query: { lat, lng, courseId } })` |
| `frontend/src/stores/designer.ts` | Ensure `buildRenderOptions()` includes `course_name` and `hole_range` |
| `frontend/src/stores/course.ts` | Optional: add `courseId` to store for easy access |

---

## Issue 7: Cricut Export Still Not Working

### Problem
Despite the export code looking structurally correct, cricut exports produce empty/corrupt files.

### Investigation Findings
The frontend code (`designer.ts`) and backend endpoint (`render.py /render/cricut`) both look structurally sound. However, there are several potential failure points:

**Potential Bug #1 — Multi-glass response mismatch:**
- When `glass_count > 1`, the API returns `{"glasses": [{white, green, ...}, ...]}` (line ~223 of render.py)
- But the frontend expects `{white, green, tan, blue, guide}` directly (line ~310 of designer.ts)
- `data.white` would be `undefined` → `cricutSvgs.value.white = ''` (empty string)
- Download then creates an empty blob → corrupt file

**Potential Bug #2 — API error swallowed:**
- If the render endpoint throws (e.g., `compute_all_terrain_following_zones()` fails), the `catch` block sets a generic message and `cricutSvgs.value = null`
- But individual layer downloads check `cricutSvgs.value?.[layer]` which would be null → shows "generate first" message
- The root error is never surfaced

**Potential Bug #3 — SVG export (non-cricut):**
- `exportSvg()` depends on `svgContent.value` being populated
- If `renderPreview()` failed silently (API returned error, or SVG was empty string), the blob is empty
- An empty SVG blob downloads as a corrupt file

### Required Fixes

**A. Handle multi-glass cricut response:**
```typescript
const data = await res.json()
if (data.glasses) {
  // Multi-glass: use first glass for now, or combine
  cricutSvgs.value = data.glasses[currentGlass.value] || data.glasses[0]
} else {
  cricutSvgs.value = data
}
```

**B. Surface API errors:**
- Log the full error and response status to console
- Show specific error messages to user (not just "not available")
- If response is not OK, read `res.text()` and display

**C. Validate SVG content before download:**
- Check that the SVG string is non-empty and starts with `<svg` or `<?xml`
- Show error if content is invalid

**D. Verify API endpoint works standalone:**
- Test the `/api/v1/render/cricut` endpoint directly (curl or API client) to confirm it returns valid SVGs
- Check for Python exceptions in the render pipeline

### Files to Modify
| File | Changes |
|------|---------|
| `frontend/src/stores/designer.ts` | Fix multi-glass response handling; add error logging; validate SVG content before download |
| `api/app/api/v1/render.py` | Add try/catch with detailed error responses; verify all render functions return non-empty SVGs |

---

## Implementation Order

### Phase A: Unblock & Fix Broken Things
1. **Issue 7: Fix cricut export** — multi-glass response bug, error surfacing
2. **Issue 4A: Remove terrain zone artifact lines** — quick removal of the broken contour rendering
3. **Issue 6: Course title persistence** — URL params + verify render pipeline passes title

### Phase B: Layout & Spacing
4. **Issue 5: Reserve ruler space** — layout.py + glass_template.py padding changes (unblocks ruler fix)
5. **Issue 1: Stats sign layout padding** — extra left/right margins for stats boxes
6. **Issue 2: Zone minimum heights** — merge logic in scoring.py

### Phase C: Visual Polish
7. **Issue 1: Stats sign rendering** — rounded rectangle with stacked stats
8. **Issue 3: Filled fairway + water with knockouts** — fill changes + SVG masking for score numbers
9. **Issue 4B-D: Ruler score alternating rectangles** — matching the hole number style

---

## Acceptance Criteria

1. **Stats signs**: Each hole has a rounded white-outline rectangle with Par/yardage/HCP stacked on separate lines, positioned next to the hole number circle on the opposite side from the tee. Stats boxes don't overflow the canvas.
2. **Zone minimums**: No "+1/+2" combined labels. Below-green zones either have enough height or merge to the higher score.
3. **Filled features**: Fairway is solid green fill, water is solid blue fill. Score numbers inside these areas are knocked out (bare glass visible through number shape).
4. **Ruler clean**: No overlapping scores/hole numbers. Scores in alternating white/transparent rectangles. No terrain zone artifact lines. Scores cover full vertical extent of each hole.
5. **Glass ruler**: Ruler has its own reserved space on the right edge. No overlap with hole content.
6. **Course title persists**: Course name and "Holes X-Y" visible after page reload. URL contains course params.
7. **Export works**: SVG downloads contain valid SVG. Cricut layers generate and download correctly for single and multi-glass configurations.
