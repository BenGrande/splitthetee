# Task 003: End-to-End Integration + Scoring Preview Controls — DONE

## What Was Implemented

### 1. End-to-End Integration Fixes

**Render API payload restructured** to match API's expected shape:
- Body now sends `{ holes, course_name, options: { mode, glass_count, current_glass, glass_dimensions, fill_mode, hidden_layers, styles, ... } }`
- `glass_dimensions` uses snake_case keys (`glass_height`, `top_radius`, `bottom_radius`, `wall_thickness`, `base_thickness`)
- All option keys use snake_case to match API conventions
- Graceful fallback with placeholder SVG if API returns error or is unavailable

**Course data flow verified:**
- Search → select course → `loadCourse()` stores data
- "Open Designer" passes lat/lng/courseId via route query params
- Designer loads course on mount from route params
- Course name tracked in designer store for display and export

### 2. Settings Save/Load Integration

**Load Settings modal implemented:**
- "Load Settings" button opens modal overlay
- Fetches saved configs from `GET /api/v1/settings`
- Displays course name + saved date + glass count
- Click to load: applies all settings + reloads course data from lat/lng
- Close via X button or clicking outside modal
- Graceful handling of empty list

**Save Settings** continues to work with API fallback to file download.

### 3. Scoring Preview Mode

- `previewMode` type updated to `'glass' | 'rect' | 'scoring-preview'`
- Added "Scoring" button in both GlassControls and toolbar
- Sends `mode: "scoring-preview"` to render API
- API returns SVG with colored scoring zone bands overlaid on layout

### 4. Ruler Toggle

- Added `ruler` to `ALL_LAYERS` and `LAYER_LABELS`
- Ruler hidden by default in `hiddenLayers`
- Toggle in LayerControls right sidebar
- Passed to API via `hidden_layers` — when enabled, API includes ruler on right edge

### 5. Export Improvements

**Single SVG export:** Filename now includes course name: `{courseName}_glass{N}_{mode}.svg`

**Multi-glass export (Export All):**
- Added `jszip` dependency
- "Export All" button renders each glass sequentially and packages into ZIP
- Downloads `{courseName}_all_glasses.zip`
- Restores original glass selection after export

### 6. Polish & UX

**Course name in header:** Displayed prominently with glass dimension info tooltip.

**Glass template info:** Shown in header: `H: 146mm | Top: ⌀86mm | Bot: ⌀60mm`

**Keyboard shortcuts:**
- `1`, `2`, `3`, `6` — switch glass count
- `g` — glass mode, `r` — rect mode, `s` — scoring preview mode
- Only active when not focused on input/select/textarea
- Shortcut hints displayed in status bar

**Loading states:** Already present from Task 002 — spinner overlay on preview area during render.

### Files Modified
- `src/stores/designer.ts` — scoring-preview mode, ruler layer, API payload restructure, courseName tracking, exportAllSvg with jszip
- `src/views/DesignerView.vue` — load settings modal, keyboard shortcuts, export all button, course name display, glass info, scoring toolbar button
- `src/components/GlassControls.vue` — scoring-preview mode button (3 mode options)
- `src/components/LayerControls.vue` — ruler appears automatically (no code change needed, just data)
- `package.json` — added `jszip` dependency

### Tests (62 total, 8 new)
New tests:
- `previewMode accepts scoring-preview`
- `applySettings handles scoring-preview mode`
- `renderPreview sets courseName from courseData`
- `renderPreview sends options in correct API shape` (validates snake_case structure)
- `ruler is hidden by default in hiddenLayers`
- `toggling ruler layer works`
- `exportSvg uses courseName in filename`
- `includes ruler layer toggle` (LayerControls)

Updated tests:
- Layer count assertions updated to 10 (added ruler)
- Default hiddenLayers now includes ruler
- GlassControls preview mode test checks for "Scoring"

### Deviations from Spec
- None significant. All items implemented as specified.

## How to Test
1. `cd frontend && npm run dev`
2. Search for a course, click "Open Designer" — verify SVG preview renders
3. Toggle glass count (1/2/3/6), verify re-render
4. Click "Scoring" mode in toolbar — verify scoring zone bands
5. Toggle ruler in right sidebar layers — verify ruler on SVG
6. Click "Export SVG" — verify `{courseName}_glass1_glass.svg` download
7. Click "Export All" — verify ZIP download with all glasses
8. Click "Save Settings" — verify API call or file download
9. Click "Load Settings" — verify modal with saved entries
10. Try keyboard shortcuts: press `1`, `2`, `3`, `6`, `g`, `r`, `s`
11. Run `npx vitest run` — all 62 tests pass
