# Task 009: Add Blue Vinyl Layer to Cricut Export UI — DONE

## Changes Made

### `frontend/src/stores/designer.ts`
- Updated `cricutSvgs` type to include `blue` field: `{ white, blue, green, tan, guide }`
- Updated `exportCricut()` to parse `blue` from API response
- Updated `downloadCricutLayer()` type to accept `'blue'` parameter
- Updated `downloadAllCricutLayers()` to include blue layer in ZIP
- Added `'cricut-blue'` to `previewMode` type union

### `frontend/src/components/CricutExportPanel.vue`
- Added Blue Layer card with blue color swatch (`#5b9bd5`), bg `bg-blue-900/40`
- Description: "Water hazards"
- Blue layer has Preview button (switches to `cricut-blue` mode)
- Blue layer has individual Download button
- Blue layer included in Download All ZIP
- Updated layer descriptions per spec: white="Outlines, labels, ruler, zones, scores", green="Greens, tees, fairway accents", tan="Bunkers"
- Added `previewLayer('blue')` handler

### `frontend/src/views/DesignerView.vue`
- Added `C-Blu` mode button to the preview toolbar

### Test Updates
- `designer.spec.ts`: Updated `exportCricut stores SVGs on success` test to include blue layer; added `downloadCricutLayer downloads blue layer` test
- `CricutExportPanel.spec.ts`: Updated all `cricutSvgs` fixtures to include blue field; updated Preview button count to 4 (was 3); updated Download button count to 5 (was 4); added `shows Blue Layer in panel` test

## Test Results
- **150 tests pass** across 11 test files (0 failures)

## Definition of Done Checklist
1. Blue layer appears in Cricut export panel with blue color indicator ✅
2. "Download Blue" button downloads the blue water hazard SVG ✅
3. "Download All" ZIP includes blue layer alongside white/green/tan ✅
4. Blue layer label says "Water hazards" ✅
5. All existing tests pass + new tests for blue layer UI ✅
