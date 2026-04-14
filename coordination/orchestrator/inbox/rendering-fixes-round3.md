# Rendering Fixes Round 3 — Accuracy, Polish, and Bug Fixes

**Date**: 2026-04-13
**Priority**: Critical
**Screenshots**: Downloads 9:01, 9:03, 9:06 PM (2026-04-13)

**NOTE TO IMPLEMENTER**: Previous rounds of fixes have had recurring issues with incomplete implementation, bugs not caught before delivery, and features that look correct in code but don't work in practice. **Before marking ANY task as done:**
1. Run the full render pipeline end-to-end (API call → SVG output) and visually inspect the SVG
2. Test BOTH rect and glass/warped modes
3. Test with at least 2 different courses (different hole counts, different layouts)
4. Verify the exported cricut SVGs contain ALL elements (open them in a browser)
5. If you change positioning/layout logic, verify no elements overlap by inspecting the actual rendered coordinates
6. If you're unsure about a rendering detail, re-read this plan — don't guess

---

## Issue 1: Ruler Rectangles Should Have Sharp Corners and Overlap Tick Marks

### Problem
The ruler score label rectangles have rounded corners (`rx="2"`). They should be sharp-cornered solid rectangles. The rectangles should overlap/span the tick marks (not sit between them).

### Current Code
`svg.py` `_render_ruler()` lines ~263, ~275: Score label rectangles use `rx="2"` for rounded corners.

### Required Changes
- Remove `rx="2"` from all ruler score rectangles (both rect and warped modes)
- Score rectangles should span the **full width between the dual-side tick marks** — the rectangle edges align with the tick endpoints, visually overlapping them
- The tick marks become the left and right edges of the rectangle, not separate elements poking out from behind it
- Apply same fix in `_render_ruler_warped()` — use sharp-cornered rectangles (or equivalent polygons in polar space), not circles

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Remove `rx` from ruler score rects in `_render_ruler()` and `_render_ruler_warped()`; widen rects to span full tick width |

---

## Issue 2: More Space Between Green Bottom and Next Tee Top

### Problem
Score zones between holes are too compressed. The below-green zones (+1, +2) are tiny because there's not enough vertical space between one hole's green and the next hole's tee box.

### Current Code
`layout.py`: `_fix_overlaps()` uses `min_gap = 4` and `_pack_holes()` uses `target_gap = 4`. These are far too small — 4px doesn't leave room for meaningful scoring zones.

### Required Changes

**A. Increase minimum gap between holes:**
- Change `min_gap` in `_fix_overlaps()` from 4 to **25-30px**
- Change `target_gap` in `_pack_holes()` from 4 to **25-30px**
- This ensures enough vertical space between green bottom and next tee top for readable below-green scoring zones

**B. Add minimum green-to-tee distance:**
- In `_fix_overlaps()` or as a new pass: calculate the distance from each hole's lowest green feature to the next hole's highest tee feature
- If this distance is less than `MIN_INTER_HOLE_SPACE` (e.g., 30px), push the lower hole down
- This is different from `min_gap` which measures tee-to-tee; we need green-to-tee

**C. Scoring zone minimum height (from previous plan):**
- In `scoring.py`: if a below-green zone would be smaller than `MIN_ZONE_HEIGHT` (8px), merge it into the higher score zone
- Remove the "+1/+2" combined label rendering from the ruler — zones are pre-merged

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/layout.py` | Increase `min_gap` and `target_gap` to 25-30px; add green-to-tee distance enforcement |
| `api/app/services/render/scoring.py` | Add MIN_ZONE_HEIGHT; merge small zones to higher score |
| `api/app/services/render/svg.py` | Remove "+1/+2" combined label logic |

---

## Issue 3: Hole Stats Boxes Overlap Fairway — Fix Positioning

### Problem (visible in 9:01/9:03 screenshots)
Stats boxes for holes 2, 3, 4 overlap directly on top of the fairway features. The stats box should be on the **outside edge** of the layout — on the opposite side of the hole number from the tee, pushed toward the canvas margin where there's empty space.

### Current Code
`svg.py` `_render_hole_stats()` lines ~395-400: Stats positioned at `hole_num_x + cr + 2` or `hole_num_x - cr - 2 - box_w` based on `direction`. But this doesn't account for where the fairway features actually are.

### How the Zigzag Layout Works
Holes zigzag left-to-right across the canvas:
- Odd-indexed holes go LEFT to RIGHT (tee on left, green on right)
- Even-indexed holes go RIGHT to LEFT (tee on right, green on left)

### Required Positioning Logic
The stats box should ALWAYS go on the side with more empty space (toward the canvas edge):

- **Holes going left-to-right** (tee on left):
  - Hole number circle is near the tee (left side)
  - Stats box goes to the **LEFT** of the hole number (further toward the left margin, AWAY from the fairway)
  - Layout: `[stats sign] ← (hole#) ← [tee box] ---- fairway ---- [green]`

- **Holes going right-to-left** (tee on right):
  - Hole number circle is near the tee (right side)
  - Stats box goes to the **RIGHT** of the hole number (further toward the right margin, AWAY from the fairway)
  - Layout: `[green] ---- fairway ---- [tee box] → (hole#) → [stats sign]`

**Key principle**: The stats box is always on the OUTER side of the tee, pushing toward the canvas edge, never overlapping the fairway.

### Text Size
- Current font is 4-5px which may be appropriate for the glass scale but the box itself (30px wide) is too prominent
- Reduce box width to 24px
- Font size: 3.5px (glass mode), 4.5px (rect mode)
- Keep the stacked format (Par / yd / HCP on separate lines)

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Rewrite stats positioning: always place on outer side of tee (toward canvas margin), away from fairway; reduce box width and font size |

---

## Issue 4: Course Name Does Not Persist on Reload

### Problem
User reports course name disappears on page reload despite URL persistence code existing.

### Investigation
The code at `DesignerView.vue` line ~43-58 DOES call `router.replace()` with courseId, lat, lng. And `onMounted()` reads these back. However:

**Potential Bug #1**: The API endpoint `/api/v1/course-holes` may not return `courseName` in its response when called with lat/lng/courseId (as opposed to the initial search flow). Verify the endpoint includes `courseName` in ALL response paths.

**Potential Bug #2**: `renderPreview()` passes `course_name: courseData.courseName` in the POST body (line ~168). But the render API endpoint may be reading it from `options` (which comes from `buildRenderOptions()`) instead of the top-level body. Check: does `render.py`'s render endpoint read `course_name` from `data.get("course_name")` or from `options.get("course_name")`?

**Potential Bug #3**: The `hole_range` (e.g., "Holes 1-6") may not be computed and passed at all. Check if it's included in the render request.

### Required Fixes
1. **Verify API response**: Ensure `/api/v1/course-holes` always returns `courseName` field
2. **Verify render endpoint reads course_name**: Check where `render.py` reads course_name from the request body and passes it to `render_svg()`
3. **Add hole_range to render options**: Compute "Holes X-Y" from the current glass's hole refs and pass it through
4. **Add console.log debugging**: Temporarily add logging to trace the course_name flow from selection → URL → reload → API → render
5. **Test the full flow**: Select course → verify URL updates → reload page → verify course data loads → verify course name renders on SVG

### Files to Modify
| File | Changes |
|------|---------|
| `frontend/src/views/DesignerView.vue` | Verify URL persistence works; add hole_range computation |
| `frontend/src/stores/designer.ts` | Ensure renderPreview passes both course_name and hole_range |
| `api/app/api/v1/render.py` | Verify course_name is read from request and passed through to svg renderer |
| `api/app/api/v1/holes.py` | Verify courseName is always in the response |

---

## Issue 5: Glass Ruler Is Completely Broken

### Problem (visible in 9:03 screenshot)
The ruler on the right edge of the glass view is a mangled white mess — overlapping shapes, unreadable text, bleeding into hole content. It looks like a thick white band of noise.

### Root Cause Analysis
`_render_ruler_warped()` transforms ruler elements to polar coordinates but:
1. Score labels use **circles** (radius 4px) instead of the rectangular design used in rect mode
2. The polar transformation causes labels at different radii to stack/overlap
3. The reserved right-side space (currently set via warp function) may still be insufficient
4. Hole number badges and score circles compete for the same angular space

### Required Changes

**A. Completely rewrite `_render_ruler_warped()`:**
- Match the rect ruler's visual design as closely as possible:
  - **Hole numbers on left** in alternating solid/outline rectangles, text rotated sideways
  - **Score labels** in alternating solid/outline sharp-cornered rectangles
  - **Dual-side tick marks** at zone boundaries
  - **Spine line** along the right edge
- In polar space, "left" = more inward (smaller radius), "right" = more outward (larger radius)
- Rectangles become **trapezoids** in polar space (wider at outer radius, narrower at inner)
- Tick marks become **radial lines** extending inward and outward from the spine

**B. Ensure adequate space:**
- The right-side reserve in `glass_template.py` warp function should be at least **12%** (currently ~8-10% from previous fix attempt, was originally 2%)
- Test that this gives the ruler enough angular width to render cleanly
- If 12% isn't enough, go to 15%

**C. Scale ruler elements to glass size:**
- Font sizes must be proportional to the glass sector size, not fixed px values
- Test at different glass dimensions to ensure readability
- Minimum font size: 3px (below this, don't render the label)

**D. Anti-overlap logic:**
- After computing all label positions in polar space, check for overlap
- If two labels would overlap: merge the smaller zone's label into the adjacent zone, or hide it
- Never render overlapping text — better to skip a label than make it unreadable

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Complete rewrite of `_render_ruler_warped()` matching rect ruler design in polar space |
| `api/app/services/render/glass_template.py` | Increase right-side reserve to 12-15% |

---

## Issue 6: Thinner White Outlines Around Holes

### Problem
The white feature outlines (fairway, rough, etc.) are too thick, making the glass view look heavy/cluttered.

### Current Code
Vinyl preview mode in `svg.py`:
- `_WHITE_CATS` (fairway, rough, path, course_boundary): stroke-width 0.8
- Green features: stroke-width 1.0
- Water: stroke-width 0.8

### Required Changes
- Reduce vinyl preview stroke widths:
  - Fairway/rough/path/course_boundary: **0.4** (was 0.8)
  - Green outlines: **0.6** (was 1.0)
  - Water outlines: **0.5** (was 0.8)
- Apply same reductions to cricut white layer outlines
- The filled features (fairway green fill, water blue fill) should have **no stroke** or very thin stroke (0.2) — the fill itself defines the shape, a thick stroke around it doubles the visual weight

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Reduce stroke-widths in vinyl preview mode |
| `api/app/services/render/cricut.py` | Reduce stroke-widths in cricut white layer |

---

## Issue 7: Score Numbers Missing from Course (Glass View)

### Problem
There are NO score numbers rendered on the actual course/holes in glass view. The previous plans discussed rendering small white numbers inside each scoring zone on the fairway, with dotted leader lines for zones too small to fit a number. This was never implemented.

### What Should Exist
Each scoring zone on the course should display its score number:
- **Inside the zone** if the zone is large enough (number fits within the zone polygon)
- **Outside with a dotted leader line** if the zone is too small
- Numbers should be white, small (3-4px font in glass mode)
- Numbers inside filled features (green fairway, blue water) should be **knocked out** (cut from the vinyl — the number is bare glass showing through)

### Implementation

**A. Determine label placement per zone:**
- For each terrain-following scoring zone, compute its centroid and area
- If area > threshold (e.g., zone can fit a 4px character): place number at centroid
- If area < threshold: place number outside the zone boundary with a dotted line from number to zone centroid

**B. Render score numbers:**
- In `_render_vinyl_preview()`: after rendering features, render score numbers as white text
- For numbers inside filled fairway/water: use SVG `<mask>` to knock out the number shape from the fill
- For numbers outside: render as white text with a `stroke-dasharray` leader line

**C. Render in cricut layers:**
- White layer: score numbers as cut text
- Green layer: knocked-out numbers where they overlap fairway fills
- Blue layer: knocked-out numbers where they overlap water fills

### Dependency
This requires the terrain-following scoring zone system to be working and providing zone polygons. If that system isn't producing valid polygons yet, implement simple horizontal-band zone labels as a fallback:
- For each zone (y_top to y_bottom), place the score number at the horizontal center of the hole's fairway at y_mid of the zone

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Add score number rendering inside zones on the course; knockout masks for filled features; leader lines for small zones |
| `api/app/services/render/cricut.py` | Add knocked-out score numbers to green and blue layers |
| `api/app/services/render/scoring.py` | Ensure zone computation provides label_position and area for each zone |

---

## Issue 8: Remove Fake Green Glow / Concentric Green Shapes — Glass Must Be Print-Accurate

### Problem (visible in 9:06 zoomed screenshot)
The green area shows multiple concentric lighter green shapes inside it — these are terrain zone contour artifacts rendered as filled green polygons. There's also an amber "glow" effect (`rgba(255,180,50,0.15)`) around greens simulating beer visibility. Neither of these would be printed on the actual glass.

### The Rule
**The glass preview must show ONLY what will physically be printed.** Nothing more, nothing less. The four vinyl colors (white, blue, green, tan) on a transparent/dark background. No glows, no fake transparency effects, no simulation of beer.

### Required Changes

**A. Remove the amber glow around greens:**
- In `_render_vinyl_preview()` (line ~510-521): Remove the `rgba(255,180,50,0.15)` fill under green features
- Green outlines should be green stroke on dark background — that's it

**B. Remove terrain zone contour fills from green area:**
- The concentric shapes visible in the zoomed screenshot are terrain zones being rendered as filled shapes near/around the green
- Remove any filled terrain zone rendering that creates visible shapes in the glass preview
- Terrain zone **boundaries** (the lines between zones) should be rendered as thin white strokes — these ARE printed as scoring zone markers
- But filled zone polygons that create concentric colored shapes must go

**C. Verify print accuracy:**
- Every visible element in glass preview must correspond to a cut vinyl piece
- Background = dark/transparent (represents clear glass, NOT beer)
- White elements = white vinyl cuts
- Green elements = green vinyl cuts (outlines only — green interiors are bare glass)
- Blue elements = blue vinyl cuts (filled)
- Tan elements = tan vinyl cuts (filled)
- NOTHING ELSE should be visible

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Remove amber glow; remove filled terrain zone polygons from vinyl preview; keep only white stroke zone boundaries |

---

## Issue 9: Cricut Export Missing Ruler and Course Name

### Problem
The exported cricut SVGs don't include the ruler (in glass/warped mode) or the course name isn't showing up.

### Current Code
- `cricut.py` `render_cricut_white()`: Ruler is only rendered when `not is_warped` (line ~269). Course name IS included (lines ~296-322) but may have the same persistence bug as Issue 4.
- The warped ruler was intentionally skipped, probably because `_render_ruler_warped()` was broken. Now that we're fixing it (Issue 5), we need to include it.

### Required Changes

**A. Include ruler in warped cricut export:**
- Remove the `not is_warped` check in `render_cricut_white()`
- Call `_render_ruler_warped()` for warped mode exports (using the fixed implementation from Issue 5)
- The ruler is white vinyl — it belongs in the white layer

**B. Verify course name in export:**
- Ensure `course_name` is passed through the cricut render pipeline
- Check: does `render_cricut()` endpoint in `render.py` read `course_name` from the request and pass it to `render_cricut_white()`?
- Trace the full flow: frontend POST → API endpoint → render function → SVG output
- The course name should be vertical text on the left edge (same as glass preview)

**C. Include hole_range in export:**
- "Holes 1-6" text should appear below the course name
- Ensure this is computed and passed through

**D. Verify ALL print elements are in export:**
After fixing, the cricut white layer should contain:
- [ ] Feature outlines (fairway, rough, path, boundary) in white
- [ ] Scoring zone boundary lines in white
- [ ] Score numbers (knocked out or white text)
- [ ] Hole number circles with numbers
- [ ] Dashed lines from hole numbers to tees
- [ ] Hole stats boxes (rounded rect + text)
- [ ] Ruler (full design with hole numbers, score labels, ticks)
- [ ] Course name (vertical, left edge)
- [ ] Hole range text ("Holes X-Y")
- [ ] Logo (bottom)
- [ ] QR code (bottom)
- [ ] Scale reference bar

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/cricut.py` | Remove `not is_warped` guard on ruler; verify course name included; add hole_range |
| `api/app/api/v1/render.py` | Ensure course_name and hole_range flow through to cricut render functions |

---

## Implementation Order

### Phase A: Fix Broken/Misleading Things First
1. **Issue 8: Remove fake green glow and concentric shapes** — Glass must be print-accurate. This is the most misleading current issue.
2. **Issue 4: Course name persistence** — Debug and fix the full flow. Must work end-to-end.
3. **Issue 6: Thinner outlines** — Quick change, immediately improves visual clarity.

### Phase B: Layout and Spacing
4. **Issue 2: More space between holes** — Increase min_gap and add green-to-tee enforcement. This changes the overall layout so must be done before fine-tuning other positioning.
5. **Issue 3: Fix stats box positioning** — Depends on layout being correct first.

### Phase C: Ruler (Both Modes)
6. **Issue 1: Sharp corners on ruler rectangles** — Quick fix for rect mode.
7. **Issue 5: Rewrite glass ruler** — Major task, complete rewrite of `_render_ruler_warped()`.

### Phase D: Score Numbers and Export
8. **Issue 7: Score numbers on course** — Depends on zone system and layout being stable.
9. **Issue 9: Fix cricut export** — Depends on ruler and course name being fixed first.

---

## Verification Checklist (MUST complete before delivery)

After ALL changes are made, verify each item by rendering a real course (not just reading code):

### Rect Mode
- [ ] Ruler has sharp-cornered rectangles spanning tick marks
- [ ] Ruler hole numbers on left, scores on right, no overlap
- [ ] Scores go from -1 to +5 for each hole with readable labels
- [ ] Below-green zones have adequate height (no "+1/+2" merged labels)
- [ ] Stats boxes don't overlap fairway (on outer side of tee)
- [ ] Course name visible on left edge, vertical
- [ ] "Holes X-Y" visible below course name
- [ ] Feature outlines are thin and not cluttered
- [ ] Score numbers visible on the course inside zones
- [ ] No concentric green shapes or amber glow

### Glass/Warped Mode
- [ ] Ruler is readable — clean labels, no overlapping, no white noise band
- [ ] Ruler has same design language as rect mode (sharp rects, dual ticks)
- [ ] Ruler doesn't overlap with rightmost hole content
- [ ] Course name visible
- [ ] Stats boxes positioned correctly (not overlapping features)
- [ ] Green shows as green outline ONLY — no interior fill or glow
- [ ] Background is dark/transparent (NOT simulating beer)
- [ ] Score numbers visible on course
- [ ] All elements match what would be physically printed

### Export (Cricut White Layer)
- [ ] Contains ruler (in glass/warped shape)
- [ ] Contains course name
- [ ] Contains hole range text
- [ ] Contains score numbers
- [ ] Contains all feature outlines
- [ ] Contains hole number circles + dashed lines to tees
- [ ] Contains stats boxes
- [ ] SVG file is valid and renders in browser
- [ ] File downloads successfully (non-empty, non-corrupt)

### Reload Test
- [ ] Select course → URL updates with courseId/lat/lng
- [ ] Reload page → course data reloads → glass preview renders with course name
- [ ] Course name persists through full reload cycle
