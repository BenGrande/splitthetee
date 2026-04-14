# Task 005: Cricut 3-Color SVG Export (Phase 3)

## Priority: HIGH — production output format

## Prerequisites
- Phase 2 complete (scoring zones, ruler, all SVG rendering working)

## What to Build

Implement 3-color SVG export for Cricut vinyl cutting. Each color is a separate SVG file optimized for cutting.

### Cricut Export Modes

Add three new render modes to the SVG renderer:

#### `cricut-white` — White Vinyl Layer
Everything cut from white vinyl as a single continuous piece:
- All outlines (hole boundaries, feature outlines)
- Scoring arc lines around greens
- Ruler (tick marks, score labels, hole numbers)
- Hole number circles and labels
- Par/yardage/handicap stats text
- Course name text (left edge, vertical)
- Hole range text (left edge)
- QR code placeholder (bottom-right area)
- One Nine logo placeholder (bottom-left area)
- All strokes should be converted to cut paths (no fills, just outlines)
- Single continuous SVG — this goes on one sheet of transfer tape

#### `cricut-green` — Green Vinyl Layer
Green/tee features arranged compactly for efficient Cricut cutting:
- Green outlines (hollow — the interior is cut OUT so bare glass shows through for beer visibility)
- Tee box shapes (solid outlines)
- Fairway accent outlines (simplified)
- **Compact arrangement**: Features are NOT in their glass layout positions. Instead, arrange them tightly in a grid/strip to minimize vinyl waste.
- Each piece labeled with a small reference number for manual placement
- Registration marks or guide showing where each piece goes on the glass

#### `cricut-tan` — Tan Vinyl Layer
Bunker shapes arranged compactly:
- All bunker features from all holes
- **Compact arrangement**: Same as green layer — tightly packed for efficient cutting
- Labeled with reference numbers
- Registration/placement guide

### Implementation

**`api/app/services/render/cricut.py`** (new file):

```python
def render_cricut_white(layout, zones_by_hole, template, opts) -> str:
    """Render white vinyl layer SVG — single continuous cut piece."""

def render_cricut_green(layout, opts) -> str:
    """Render green vinyl layer SVG — compact arrangement of green/tee pieces."""

def render_cricut_tan(layout, opts) -> str:
    """Render tan vinyl layer SVG — compact arrangement of bunker pieces."""

def _compact_arrange(pieces, canvas_width, padding=5) -> list:
    """Arrange SVG pieces in a compact grid layout for efficient cutting.
    Uses a simple bin-packing: sort by height descending, place left-to-right
    in rows, wrap to next row when width exceeded."""

def _extract_features_by_category(layout, categories) -> list:
    """Extract all features of given categories from all holes."""
```

**Compact arrangement algorithm:**
1. Extract all features of the target categories from all holes
2. Compute bounding box for each feature
3. Sort by height descending (tall pieces first)
4. Pack into rows: place left-to-right with padding, wrap when row exceeds canvas width
5. Each piece gets a reference label (e.g., "G1" for green on hole 1, "B3" for bunker on hole 3)
6. Output SVG with pieces arranged in their compact positions

**White layer specifics:**
- Convert all features to outline-only (stroke, no fill)
- Stroke width: 0.5px (hairline for cutting)
- Text elements use a Cricut-compatible font
- All elements in their actual glass layout positions (this is one continuous piece)
- For glass mode: elements positioned on the unwrapped glass sector shape

### API Endpoint Updates

Update `POST /api/v1/render` to support new modes:
- `mode: "cricut-white"` → returns white layer SVG
- `mode: "cricut-green"` → returns green layer compact SVG
- `mode: "cricut-tan"` → returns tan layer compact SVG
- `mode: "cricut-all"` → returns all three layers: `{ white_svg, green_svg, tan_svg }`

Add dedicated endpoint:
```
POST /api/v1/render/cricut
Body: { holes, options (same as render) }
Returns: { white: "<svg>...", green: "<svg>...", tan: "<svg>...", guide: "<svg>..." }
```

The `guide` SVG is a placement reference showing the full glass layout with colored outlines indicating where each numbered green/tan piece goes.

### Scale Verification

Add a 1:1 scale ruler element to each Cricut SVG:
- A 10mm reference bar at the bottom of each SVG
- Labeled "10mm — print at 100% scale"
- Allows user to verify Cricut is cutting at correct size

### SVG Requirements for Cricut
- Use `mm` units in SVG viewBox (not px)
- Convert all dimensions to real-world mm based on glass template
- No transparency/opacity (Cricut ignores it)
- Strokes only, no fills (Cricut cuts along paths)
- Clean, non-overlapping paths
- Minimal point count (simplify complex polygons if needed)

## Files to Create/Modify
- CREATE: `api/app/services/render/cricut.py`
- MODIFY: `api/app/api/v1/render.py` (add cricut modes + dedicated endpoint)
- MODIFY: `api/app/services/render/svg.py` (may need to extract shared helpers)

## Definition of Done
- [ ] `cricut-white` mode produces outline-only SVG in glass layout positions
- [ ] `cricut-green` mode produces compact arrangement of green/tee pieces
- [ ] `cricut-tan` mode produces compact arrangement of bunker pieces
- [ ] Compact arrangement minimizes wasted vinyl space
- [ ] Reference labels on green/tan pieces for manual placement
- [ ] `POST /api/v1/render/cricut` returns all three layers + placement guide
- [ ] SVG uses mm units at correct scale
- [ ] Scale verification ruler included
- [ ] Tests cover all three render modes and compact arrangement

## Done Report
When complete, write your done report to: `coordination/api/outbox/005-done.md`
