# Task 002: Port Glass Designer View — DONE

## What Was Implemented

### Files Created
- **`src/stores/designer.ts`** — Pinia store with all designer state and actions
- **`src/components/GlassControls.vue`** — Glass config, dimensions, fill mode, view, text/logo controls
- **`src/components/LayerControls.vue`** — Layer visibility toggles + per-layer style editor (color pickers, stroke width)
- **`src/components/SvgPreview.vue`** — SVG display with mouse pan/zoom interaction

### Files Modified
- **`src/views/DesignerView.vue`** — Full three-column layout replacing stub

### Features Implemented

**Three-column layout:**
1. **Left sidebar (300px)** — Course search (debounced), glass count selector (1/2/3/6), glass dimension inputs (height, top/bottom radius, wall/base thickness), fill mode (full/can/custom), current glass selector, preview mode toggle (glass/rect), font selector (17 Google Fonts), show text toggle, per-hole color toggle, logo upload with preview/clear
2. **Center preview area** — SVG preview with pan (mouse drag) and zoom (mouse wheel), toolbar with glass selector, mode toggle, reset zoom button, loading spinner overlay
3. **Right sidebar (200px)** — Layer toggles with color swatches for all 9 layers, per-layer style editor with fill/stroke color pickers and stroke width inputs

**State management (designer store):**
- All state: glassCount, currentGlass, glassDimensions, fillMode, previewMode, hiddenLayers, styles, fontFamily, logoDataUrl, showText, perHoleColors, svgContent, loading, statusMessage
- Actions: toggleLayer, updateStyle, setLogo, renderPreview, exportSvg, saveSettings, loadSettings, loadSettingsList, applySettings
- Exports: ALL_LAYERS, LAYER_LABELS, DEFAULT_STYLES, FONT_OPTIONS

**API integration:**
- `POST /api/v1/render` for SVG preview (graceful fallback with placeholder SVG if unavailable)
- `POST /api/v1/settings` for save (falls back to file download)
- `GET /api/v1/settings` and `GET /api/v1/settings/:id` for load
- Route params: loads course from `?lat=...&lng=...&courseId=...`

**Debounced re-render:** 300ms debounce on any state change, watching all relevant reactive properties.

**Bottom action bar:** Export SVG download + Save Settings with API/file fallback.

**Status bar:** Shows current glass/mode info and API status messages.

### Tests (36 new, 54 total)
- `designer.spec.ts` — 18 tests: defaults, toggleLayer, updateStyle, setLogo, renderPreview (success, failure, no-data), applySettings, exports
- `GlassControls.spec.ts` — 8 tests: glass count buttons, dimension inputs, fill mode, preview mode, fonts, checkboxes
- `LayerControls.spec.ts` — 6 tests: layer toggles, labels, defaults, store integration, color pickers, stroke inputs
- `SvgPreview.spec.ts` — 5 tests: empty state, SVG render, loading overlay, resetZoom

### Deviations from Spec
- "Export All" (ZIP download) deferred — requires a ZIP library not in deps; single SVG export works
- "Load Settings" modal listing saved configs deferred — save/load via API endpoints ready, modal UI can be added when API is confirmed working

## How to Test
1. `cd frontend && npm run dev`
2. Navigate to `/designer` or click "Open Designer" from search results
3. Verify three-column layout renders
4. Adjust glass dimensions, count, fill mode — confirm state updates
5. Toggle layers on/off, change colors/stroke widths
6. Switch preview mode glass/rect
7. Pan (drag) and zoom (scroll) the preview area
8. Click "Export SVG" — downloads file
9. Run `npx vitest run` — all 54 tests pass
