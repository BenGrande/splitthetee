# Rendering Fixes Round 4 — Ruler, Layout, Export Parity

**Date**: 2026-04-13
**Priority**: Critical
**Screenshots**: Downloads 9:36, 9:40 PM (2026-04-13)

**CRITICAL INSTRUCTION TO IMPLEMENTER**: The previous three rounds of plans have had persistent issues with incomplete implementation and bugs. This round MUST be implemented correctly. The core principle is simple:

> **The glass preview and the cricut white layer export must render the EXACT same elements in the EXACT same positions.** They are two views of the same thing.

Currently `render_cricut_white()` in `cricut.py` is a completely separate rendering pipeline from `_render_vinyl_preview()` in `svg.py`. This is the root cause of the export not matching the preview. **The fix is to share rendering logic**, not maintain two divergent codepaths.

---

## Issue 1: Ruler Score Rectangles — Sharp Corners, No Vertical Spine Behind Them

### Problem
Score label rectangles on the ruler have rounded corners (`rx="2"`). The vertical spine line is visible behind/through the score rectangles.

### Required Changes
- **Remove `rx` attribute** from all score label rectangles in both `_render_ruler()` and `_render_ruler_warped()`
- **Hole number rectangles CAN keep rounded corners** with small spacing between them
- **Remove the vertical spine line** from behind the score area — the score rectangles themselves form the visual column. The spine should only be visible in gaps between score rectangles (if any), or removed entirely
- Score rectangles should span the full width between the dual-side tick mark endpoints — ticks become the left/right edges of the rectangle

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | `_render_ruler()`: remove `rx` from score rects, remove spine line behind scores; `_render_ruler_warped()`: same |

---

## Issue 2: Ruler Hole Numbers and Scores Must Not Overlap

### Problem
Hole number rectangles and score rectangles on the ruler overlap vertically. Each should occupy distinct, non-overlapping vertical space.

### Required Changes
The ruler layout for each hole should be:

```
┌──────────┐
│  HOLE 1  │  ← hole number rectangle (rounded corners OK, small gap below)
└──────────┘
┌──────────┐
│    +5    │  ← score rectangle (sharp corners, no gap between scores)
├──────────┤
│    +4    │
├──────────┤
│    +3    │
├──────────┤
│    +2    │
├──────────┤
│    +1    │
├──────────┤
│     0    │
├──────────┤
│    -1    │
├──────────┤
│    +1    │  ← below-green
├──────────┤
│    +2    │  ← below-green
└──────────┘
┌──────────┐
│  HOLE 2  │  ← next hole
└──────────┘
...
```

- Hole number rectangle occupies a fixed height at the TOP of each hole's ruler section
- Score rectangles stack below it, each spanning its zone's y_top to y_bottom
- **No vertical overlap** — hole number rect ends before first score rect begins
- Small gap (2-3px) between hole number rect and first score rect
- Score rects are flush against each other (no gaps between scores)

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Rewrite ruler layout to ensure hole numbers and scores occupy distinct vertical bands |

---

## Issue 3: Glass Ruler Is Broken — Elements Not Rotating With Curvature

### Problem (visible in 9:36 screenshot)
The ruler elements on the glass view are rendered as flat horizontal rectangles/text placed at polar coordinates. They are NOT rotated to follow the glass curvature. This creates a chaotic white mess on the right edge.

### Root Cause
In `_render_ruler_warped()` (svg.py) and in `cricut.py` (lines 269-314), ruler elements are placed at polar (r, angle) positions but the rectangles and text are not rotated. A rectangle at angle θ needs to be rotated by θ to align tangentially with the glass arc.

In `cricut.py` specifically (the export), the warped ruler code (lines 269-314) places tick marks and text at the edge angle but:
- Tick marks are straight lines extending radially — this is correct
- Text labels are placed at (x, y) with `text-anchor="start"` but NO rotation — they render horizontally, not following the curve
- There are no rectangles at all — just plain text and tick lines

### Required Changes

**A. Every ruler element must be rotated to follow the glass curvature:**
- At any point on the glass edge at angle θ, elements must be rotated by `θ × 180/π` degrees
- Rectangles become rotated rectangles (use `transform="rotate(angle, cx, cy)"`)
- Text must also be rotated to read along the glass edge
- Tick marks (radial lines) are already correct — they extend inward/outward from the edge

**B. Use `transform="rotate()"` on all elements:**
For an element at angle θ on the glass edge:
```svg
<g transform="rotate({angle_degrees}, {cx}, {cy})">
  <rect .../>  <!-- positioned as if at angle=0, rotation handles orientation -->
  <text .../>
</g>
```

Or equivalently, compute the rotation angle for each element:
```python
angle_deg = math.degrees(edge_angle)  # for right edge
# Each element at radius r gets placed at:
x = r * sin(edge_angle)
y = -r * cos(edge_angle)
# And rotated by angle_deg around its center
```

**C. Apply to BOTH `svg.py` `_render_ruler_warped()` AND `cricut.py` warped ruler code.**

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Rewrite `_render_ruler_warped()` — add rotation transforms to all elements |
| `api/app/services/render/cricut.py` | Rewrite warped ruler section (lines 269-314) — add rotation transforms, match glass preview design |

---

## Issue 4: Content Overflows Glass — Reduce Horizontal Spread

### Problem (visible in 9:36 screenshot)
Holes extend too far horizontally, causing:
- Hole 5's stats box cut off at right edge
- Hole 1's content clipped at top
- Overall layout feels cramped against the glass boundaries

### Root Cause
The layout engine spreads holes across the full draw width. The glass warp then maps this to the sector, but the sector's usable area is smaller than the rectangular draw area (especially at top/bottom where the sector narrows).

### Required Changes

**A. Reduce max_hole_width:**
- In `layout.py`: reduce `max_hole_width` from 0.55 to **0.40-0.45**
- This makes each hole take up less horizontal space, leaving more margin

**B. Increase warp padding:**
- In `glass_template.py`: increase the content padding from 12px to **20px**
- Increase edge_inset from 3% to **5%** (more breathing room from glass edges)

**C. Increase text_reserve and right reserve:**
- Left text_reserve: increase from 6% to **10%** (more room for course name + stats boxes on left holes)
- Right reserve: increase from current value to **15%** (room for ruler + stats boxes on right holes)

**D. Clip check:**
- After computing warped positions, check if any element extends beyond the glass clip area
- If stats boxes would be clipped, move them inward or reduce their size

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/layout.py` | Reduce `max_hole_width` default |
| `api/app/services/render/glass_template.py` | Increase padding, edge_inset, text_reserve, right reserve |

---

## Issue 5: White Outlines Still Too Thick

### Problem
Feature outlines (fairway, rough, etc.) are still visually heavy in the glass view.

### Current Values (from svg.py vinyl preview)
- `_WHITE_CATS`: stroke-width 0.8
- Green: stroke-width 1.0
- Water: stroke-width 0.8

### Required Changes
Reduce ALL vinyl preview stroke widths:
- Fairway/rough/path/boundary outlines: **0.3** (was 0.8)
- Green outlines: **0.4** (was 1.0)
- Water outlines (if outline visible around fill): **0.2** (was 0.8)
- Bunker outlines: **0.2**
- Tee outlines: **0.3**

Also reduce in cricut.py white layer:
- Feature outlines: **0.3** (was 0.4, line 173 `sw = "0.4"`)

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Reduce stroke-widths in vinyl preview |
| `api/app/services/render/cricut.py` | Reduce stroke-width in white layer (line 173) |

---

## Issue 6: Course Name Needs More Padding on Left

### Problem
The course name text ("Athabasca Golf & Country Club") is pressed against the left edge of the glass with no breathing room.

### Current Code
In `svg.py` `_render_warped_text()`: text paths use offset `0.01` from the left edge (basically touching the edge).

### Required Changes
- Increase the left text path offset from `0.01` to **0.03-0.04** (3-4% of sector angle from the left edge)
- This pushes the course name inward, giving visual breathing room
- Apply same fix in `cricut.py` course name rendering (line 346: `angle = -half_a + 0.01` → change to `0.03`)

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Increase text path offsets in `_build_text_paths()` |
| `api/app/services/render/cricut.py` | Increase text arc offset (line 346) |

---

## Issue 7: Hole 1 Stats Cut Off at Top / Hole 5 Stats Cut Off at Right

### Problem
Stats boxes for edge holes extend beyond the glass clip area and get truncated.

### Required Changes
- Before rendering a stats box, check if it would extend beyond the glass outline (or beyond the canvas in rect mode)
- If it would be clipped:
  - **Option A**: Move the box inward (reduce the offset from the hole number)
  - **Option B**: Place it on the other side of the hole number (toward the fairway) — better to overlap slightly with features than to be invisible
  - **Option C**: Reduce font size and box dimensions for edge holes
- For the first and last holes specifically: bias the stats box toward the interior of the glass

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Add boundary checking for stats boxes; fallback positioning for edge holes |

---

## Issue 8: No "Holes X-Y" Text Under Course Name

### Problem
The hole range text (e.g., "Holes 1-6") is not visible under the course name in glass mode.

### Current Code
In `svg.py` `_render_warped_text()`: the `hole_range` text IS rendered along `textArc2`. But in `cricut.py` (line 370-373), the warped hole_range rendering is just `pass` — explicitly skipped.

Also, the hole_range may not be computed/passed in the first place. Check `designer.ts` `renderPreview()` and `exportCricut()`.

### Required Changes
1. **Frontend**: Compute `hole_range` (e.g., "Holes 1-6") from the current glass's hole refs and pass it in the render request
2. **svg.py**: Verify `hole_range` renders in warped mode — check if `textArc2` is properly defined and positioned
3. **cricut.py**: Implement the warped hole_range rendering (line 370-373) instead of `pass` — render along a text arc slightly offset from the course name arc

### Files to Modify
| File | Changes |
|------|---------|
| `frontend/src/stores/designer.ts` | Compute and pass `hole_range` in render requests |
| `api/app/services/render/svg.py` | Verify hole_range warped rendering works |
| `api/app/services/render/cricut.py` | Implement warped hole_range (replace `pass` on line 373) |

---

## Issue 9: No Scoring Zone Boundaries or Score Numbers on Course

### Problem
No scoring zone boundary lines visible on the course layout. No score numbers inside zones. This was discussed in previous plans but never implemented for the glass view.

### Required Changes
This is carried forward from Round 3, Issue 7. The implementation needs:

1. **Zone boundary lines on course**: Thin white lines at each zone boundary, crossing the fairway/hole width
2. **Score numbers**: Small white numbers inside each zone (or outside with dotted leader line if too small)
3. **Knockout from filled features**: Numbers inside green fairway or blue water should be cut out

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Render zone boundaries and score numbers on course in vinyl preview |
| `api/app/services/render/cricut.py` | Include zone boundaries and score numbers in white layer |

---

## Issue 10: Ruler Wedge Compression at Bottom of Glass

### Problem
The glass sector narrows toward the bottom (inner radius), causing ruler elements for lower holes to be extremely compressed and unreadable.

### Required Changes
- **Adaptive sizing**: Font size and rectangle height should scale with the available radial space at each position
- At the bottom of the glass (smaller radius), the angular width is less, so elements need to be proportionally smaller or the minimum readable size should be enforced
- If a score label can't fit legibly at a given radial position, either:
  - Skip it (don't render unreadable text)
  - Render it as a small tick mark only (no text)
  - Or consolidate multiple scores into a range label
- Consider: the ruler occupies a fixed angular slice. At the top (outer_r) this slice is wide in mm. At the bottom (inner_r) the same angular slice is much narrower. Account for this.

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Add adaptive sizing in `_render_ruler_warped()` based on radius |

---

## Issue 11: Export Does Not Match Glass Preview — Root Cause Fix

### Problem (visible comparing 9:36 and 9:40 screenshots)
The cricut white layer export looks completely different from the glass preview:
- Export has condensed inline stats ("P4 356y H5") instead of the box design
- Export has a basic tick-mark ruler instead of the full rectangle design
- Export has thin uniform white outlines instead of filled green/blue features
- Export is missing many elements the glass preview has

### Root Cause
`render_cricut_white()` in `cricut.py` is a **separate, independent rendering pipeline** from `_render_vinyl_preview()` in `svg.py`. They were written at different times and have diverged. Every time a rendering improvement is made to the glass preview, it needs to be separately re-implemented in the cricut export — and it hasn't been.

### Required Fix — Architectural

**The cricut white layer should be generated by the SAME code that generates the glass preview**, with minor modifications (no background, no colored fills — those go in their respective color layers).

**Option A (Recommended): Refactor `_render_vinyl_preview()` to accept a "layer" parameter:**
```python
def _render_vinyl_preview(layout, opts, ..., layer="all"):
    # layer="all" → full glass preview (current behavior)
    # layer="white" → only white elements (for cricut white export)
    # layer="green" → only green elements (for cricut green export)
    # etc.
```

This ensures the glass preview and cricut export are always in sync because they use the same rendering function.

**Option B: Have `render_cricut_white()` call `_render_vinyl_preview()` with a filter:**
```python
def render_cricut_white(layout, zones_by_hole, template, opts):
    # Generate using the same function as glass preview
    return _render_vinyl_preview(layout, {
        **opts,
        "cricut_mode": True,  # no background, no colored fills
        "cricut_layer": "white",
    }, ...)
```

**Whichever option is chosen**, the result must be: **what you see in the glass preview is exactly what comes out in the export.**

### What Each Cricut Layer Should Contain

**White layer** (matches all white elements in glass preview):
- Feature outlines (fairway, rough, path, boundary) — white strokes at same width as preview
- Scoring zone boundary lines — white
- Score numbers on course — white (or knocked out of colored fills)
- Hole number circles + numbers — white
- Dashed lines from hole numbers to tees — white
- Stats boxes (rounded rect + stacked text) — white, SAME DESIGN as preview
- Ruler (full design with hole numbers + score rectangles + ticks) — white
- Course name (vertical on left) — white
- Hole range text — white
- Logo — white
- Glass outline — white

**Green layer** (matches all green elements in glass preview):
- Fairway fills — solid green
- Green outlines — green stroke
- Tee box shapes — green
- Score number knockouts where they overlap fairway

**Blue layer** (matches all blue elements in glass preview):
- Water fills — solid blue
- Score number knockouts where they overlap water

**Tan layer** (matches all tan elements in glass preview):
- Bunker fills — tan

**Guide layer**: Reference overlay showing where all colored pieces go.

### Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Refactor `_render_vinyl_preview()` to accept layer parameter for cricut export |
| `api/app/services/render/cricut.py` | Rewrite `render_cricut_white()` to use shared rendering logic; update green/blue/tan layers to match preview fills |

---

## Implementation Order

### Phase A: Architecture Fix (must be done first — everything else depends on this)
1. **Issue 11: Unify glass preview and cricut export rendering** — This is THE most important change. Once the white layer uses the same code as the glass preview, all subsequent fixes automatically apply to both.

### Phase B: Ruler Fix (second priority — most visible broken thing)
2. **Issue 3: Rotate ruler elements on glass** — Transform all elements to follow curvature
3. **Issue 1: Sharp corners on score rects, remove spine** — Quick visual fix
4. **Issue 2: Hole numbers and scores non-overlapping** — Layout fix
5. **Issue 10: Adaptive sizing at bottom of glass** — Prevents compression

### Phase C: Layout and Spacing
6. **Issue 4: Reduce horizontal spread** — More padding, narrower holes
7. **Issue 7: Stats box clipping** — Boundary checking
8. **Issue 6: Course name padding** — Increase text path offset
9. **Issue 5: Thinner outlines** — Reduce stroke widths

### Phase D: Content Completeness
10. **Issue 8: Hole range text** — Compute and render "Holes X-Y"
11. **Issue 9: Score numbers on course** — Zone boundaries + labels

---

## Verification Checklist (MANDATORY before delivery)

**Test with a real course (Athabasca Golf & Country Club or similar). Do NOT skip these checks.**

### Glass Preview
- [ ] Course name visible with padding from left edge
- [ ] "Holes X-Y" visible below course name
- [ ] Ruler on right edge: elements rotate to follow glass curvature
- [ ] Ruler: hole numbers and scores in separate non-overlapping vertical bands
- [ ] Ruler: score rectangles have sharp corners
- [ ] Ruler: no vertical spine line visible behind score rectangles
- [ ] Ruler: readable at bottom of glass (not compressed to nothing)
- [ ] No content clipped by glass edges (stats boxes, hole numbers all visible)
- [ ] White outlines are thin and clean
- [ ] Fairway filled green, water filled blue, bunkers filled tan
- [ ] Green outlines are green stroke only (no fill, no glow)
- [ ] Scoring zone boundaries visible as thin white lines on course
- [ ] Score numbers visible inside zones (or with leader lines)
- [ ] Stats boxes on outer side of tee, not overlapping fairway

### Cricut White Layer Export
- [ ] **Looks identical to the white elements in the glass preview** — same positions, same sizes, same design
- [ ] Stats boxes are rounded rectangles with stacked text (NOT condensed inline)
- [ ] Ruler matches glass preview ruler design exactly
- [ ] Course name and hole range text present
- [ ] Zone boundaries and score numbers present
- [ ] Valid SVG that opens in browser

### Cricut Green/Blue/Tan Layers
- [ ] Green layer has fairway fills matching glass preview
- [ ] Blue layer has water fills matching glass preview
- [ ] Tan layer has bunker fills matching glass preview

### Cross-Mode Consistency
- [ ] Glass preview white elements == cricut white layer (overlay them to check)
- [ ] Glass preview green elements == cricut green layer positions
- [ ] All fixes work in BOTH rect and glass modes
