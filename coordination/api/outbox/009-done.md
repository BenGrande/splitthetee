# Task 009: Vinyl Preview Mode + Course Name + Ruler + Logo in SVG Renderer — DONE

## Completed

### A. Vinyl Preview Mode (`_render_vinyl_preview()` in `svg.py`)
- New rendering path triggered by `vinyl_preview: true` in opts
- Dark amber gradient background (`#2a1f0e` → `#4a3520`) simulating beer in glass
- **White elements** (stroke only, no fill): fairway, rough, water, path, course_boundary outlines; hole numbers (circle + number); hole stats; ruler; course name
- **Green elements** (stroke only, `#4ade80`): green and tee outlines
- **Tan elements** (filled, `#d2b48c`): bunker shapes
- **Green interior**: amber glow overlay (`rgba(255,180,50,0.15)`) under green stroke outlines
- Terrain zone contours from Task 008 rendered as white stroke outlines (score > -1)

### B. Course Name — Vertical Left Strip
- Rect mode: vertical text with `rotate(-90)` transform, bottom-to-top, left edge
- Glass/warped mode: uses existing textPath along left edge of sector
- "Holes X–Y" rendered below course name in smaller text

### C. Ruler — Glass/Warped Mode (`_render_ruler_warped()`)
- New function renders ruler along the RIGHT edge of the glass wrap sector
- Vertical line from outer to inner radius along right edge angle
- Tick marks extending inward at each zone boundary
- Score labels positioned just inside ticks
- Hole number labels (H1, H2, etc.) centered in each section
- Maps y-coordinates to radial positions along the sector edge

### D. Logo Placement (`_render_logo_bottom_left()`)
- Rect mode: bottom-left corner, 20x20px, with opacity
- Glass mode: near inner arc (bottom of wrap), left side
- Graceful skip if no logo_data_url provided

### E. Mode Routing in `render.py`
- `vinyl-preview` mode sets `vinyl_preview: true` in svg_opts
- Terrain zones serialized and passed through to SVG renderer
- Existing modes completely unchanged

### Backward Compatibility
- All existing modes (`rect`, `glass`, `scoring-preview`, `cricut-*`) produce identical output
- Regression test confirms standard mode has no vinyl artifacts

### New Tests (12 tests in `tests/test_svg_renderer.py`)
- `test_dark_background` — gradient with beer color present
- `test_green_features_stroke_no_fill` — green stroke `#4ade80`
- `test_white_elements_stroke_only` — white stroke `#ffffff`
- `test_bunker_tan_fill` — tan fill `#d2b48c`
- `test_course_name_vertical_text` — rotate(-90) transform with course name
- `test_ruler_renders_in_rect_mode` — ruler with tick labels
- `test_ruler_renders_in_glass_mode` — ruler in warped layout
- `test_logo_bottom_left` — logo image element present
- `test_green_interior_amber` — amber overlay on green interiors
- `test_terrain_zone_contours` — terrain zone layer rendered
- `test_existing_modes_unchanged` — standard mode regression check
- `test_hole_numbers_present` — hole number circles and text

## Test Results
263 tests passed, 0 failed.
