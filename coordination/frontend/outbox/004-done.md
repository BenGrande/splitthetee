# Task 004: Cricut Export UI in Designer — DONE

## What Was Implemented

### 1. Cricut Export Panel (CricutExportPanel.vue)
New modal component with:
- **Four layer previews**: White (outlines/text/ruler), Green (greens/tees compact), Tan (bunkers compact), Placement Guide
- **Color-coded cards** with layer swatches and descriptions
- **SVG thumbnails** for each layer when generated
- **Per-layer download buttons** — downloads individual SVG files
- **Preview buttons** (white/green/tan) — switches main preview to that cricut layer
- **Download All (ZIP)** — packages all 4 SVGs into a ZIP via jszip
- **Scale verification info** — "Print at 100% scale — verify with 10mm reference bar"
- **Loading state** — spinner while generating cricut layers
- **Graceful fallback** — "Cricut export not yet generated" when API unavailable

### 2. Cricut Preview Modes
- `previewMode` type extended: `'cricut-white' | 'cricut-green' | 'cricut-tan'`
- Preview mode buttons added in both GlassControls (C-White, C-Green, C-Tan) and toolbar
- Sends appropriate mode to `POST /api/v1/render` for individual layer preview

### 3. API Integration
- `POST /api/v1/render/cricut` — fetches all 4 layer SVGs at once
- Response shape: `{ white, green, tan, guide }`
- Stored in `designer.cricutSvgs` reactive state
- Graceful error handling — sets null on failure, shows "not available" status

### 4. Designer Store Additions
- `cricutSvgs: { white, green, tan, guide } | null` — cached cricut layer SVGs
- `cricutLoading: boolean` — loading state for cricut generation
- `exportCricut(courseData)` — calls `/api/v1/render/cricut`, stores results
- `downloadCricutLayer(layer)` — downloads individual layer as SVG file
- `downloadAllCricutLayers()` — packages all layers + guide into ZIP
- `buildRenderOptions()` — extracted shared helper for render payloads (DRY refactor)

### 5. Placement Guide Display
- Fourth layer in the Cricut panel: "Placement Guide"
- Shows full glass layout with numbered markers
- Downloadable separately or included in ZIP

### Files Created
- `src/components/CricutExportPanel.vue`
- `src/components/__tests__/CricutExportPanel.spec.ts`

### Files Modified
- `src/stores/designer.ts` — cricut state, actions, preview modes, buildRenderOptions helper
- `src/views/DesignerView.vue` — "Export Cricut" button, CricutExportPanel import, cricut toolbar buttons
- `src/components/GlassControls.vue` — C-White/C-Green/C-Tan preview mode buttons

### Tests (79 total, 17 new)
New store tests:
- `previewMode accepts cricut modes`
- `cricutSvgs is null by default`
- `exportCricut stores SVGs on success`
- `exportCricut handles API failure gracefully`
- `exportCricut handles non-ok response`
- `exportCricut skips if no holes`
- `downloadCricutLayer does nothing when no cricut SVGs`

New CricutExportPanel tests (10):
- Renders when visible / hidden
- Placeholder when no SVGs
- Layer previews when SVGs available
- Scale verification info
- Download All button
- Close emits event
- Loading state
- Preview buttons for 3 layers
- Download buttons for 4 layers

Updated tests:
- GlassControls checks for C-White/C-Green/C-Tan buttons

### Deviations from Spec
- None. All items implemented as specified.

## How to Test
1. `cd frontend && npm run dev`
2. Open designer with a course loaded
3. Click "Export Cricut" — modal opens, calls API
4. If API available: see 4 layer previews with thumbnails
5. Click "Preview" on any layer — main preview switches to that cricut mode
6. Click "Download" on individual layers — downloads SVG
7. Click "Download All (ZIP)" — downloads ZIP with all 4 files
8. Toolbar buttons C-Wht/C-Grn/C-Tan switch preview mode
9. If API unavailable: modal shows "not yet generated" placeholder
10. Run `npx vitest run` — all 79 tests pass
