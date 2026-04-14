# Task 010: Ruler Readability Overhaul — DONE

## Completed

### 1. Increased Text Sizes
- Score labels: **8pt** (was 4pt)
- Hole number labels: **12pt** (was 8pt)
- Tick line stroke width: **1px** (was 0.5px)
- Ruler spine stroke width: **1px** (was 0.5px)

### 2. Alternating Left/Right Labels
- Even-index zones (e.g., +5, +3, +1): label and tick on the **left** side of ruler spine
- Odd-index zones (e.g., +4, +2, 0): label and tick on the **right** side
- Doubles effective vertical spacing between adjacent labels

### 3. Zone Range Bands
- Alternating opacity bands (`opacity="0.05"`) drawn behind zones
- Even-index zones get a subtle white background band
- Provides visual distinction between adjacent zones

### 4. Hole Boundary Indicators
- **Thick horizontal line** (2px stroke) at top of each hole section
- **Hole number badge**: rounded rect (`rx="4"`) with dark fill and white stroke
- Bold hole number text centered inside the badge

### 5. Compressed Below-Green Zone Handling
- Detects when below-green zones are < 8px tall each
- Combines labels into single string (e.g., "+1/+2")
- Single tick and combined label replace individual unreadable ones

### 6. Both Modes Updated
- **Rect mode** (`_render_ruler()`): fully rewritten with all improvements
- **Glass/warped mode** (`_render_ruler_warped()`): matching improvements with scaled sizes
  - Label font: 5pt (appropriate for warped geometry)
  - Hole font: 7pt
  - Badge with `rx="3"` rounded corners
  - Alternating tick directions (inward/outward from spine)
  - Combined labels for compressed below-green zones

### Backward Compatibility
- All existing tests pass unchanged
- Ruler output structure (`<g class="layer-ruler">`) preserved

### New Tests (9 tests in `tests/test_svg_renderer.py::TestRulerReadability`)
- `test_score_labels_min_font_size` — all ruler fonts >= 8pt
- `test_labels_alternate_sides` — both `text-anchor="start"` and `"end"` present
- `test_hole_boundary_thick_stroke` — 2px boundary vs 1px ticks
- `test_hole_number_badge` — rounded rect with hole number text
- `test_combined_labels_for_compressed_zones` — "+1/+2" combined label
- `test_zone_range_bands` — alternating opacity bands present
- `test_ruler_rect_mode` — ruler renders in rect mode
- `test_ruler_glass_mode` — ruler renders in warped mode with badge
- `test_ruler_spine_stroke_width` — spine has 1px stroke

## Test Results
272 tests passed, 0 failed.
