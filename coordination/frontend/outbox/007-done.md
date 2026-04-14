# Task 007: Add Vinyl Preview Mode — DONE

## Completed: 2026-04-13

## Changes Made

### `frontend/src/stores/designer.ts`
- Added `'vinyl-preview'` to the `previewMode` type union (first position)
- Changed default `previewMode` value from `'glass'` to `'vinyl-preview'`
- `buildRenderOptions()` already sends `mode: previewMode.value`, so it automatically sends `'vinyl-preview'` to the API

### `frontend/src/components/GlassControls.vue`
- Added `{ label: 'Vinyl', value: 'vinyl-preview' }` as the **first** entry in the `previewModes` array
- Vinyl button appears first in the sidebar preview mode button group

### `frontend/src/views/DesignerView.vue`
- Added Vinyl button as the **first** entry in the toolbar mode buttons (`{ value: 'vinyl-preview', label: 'Vinyl', key: 'V' }`)
- Added `v` keyboard shortcut: `case 'v': designer.previewMode = 'vinyl-preview'; break`
- Updated status bar keyboard hint from `g/r/s mode` to `v/g/r/s mode`

### `frontend/src/components/SvgPreview.vue`
- No changes needed — the component uses a dark `bg-[#111]` background already, which works well with the dark vinyl-preview SVG

## Tests Added/Updated

### `src/stores/__tests__/designer.spec.ts`
- Updated default state test: expects `previewMode` to be `'vinyl-preview'` (was `'glass'`)
- Updated render API shape test: expects `mode: 'vinyl-preview'` in payload (was `'glass'`)
- Added: `previewMode accepts vinyl-preview`
- Added: `previewMode defaults to vinyl-preview`
- Added: `render payload includes mode vinyl-preview when selected`

### `src/components/__tests__/GlassControls.spec.ts`
- Updated: existing preview mode button test now checks for 'Vinyl' in addition to other modes
- Added: `vinyl button is the first preview mode button`
- Added: `clicking Vinyl button sets store mode to vinyl-preview`

## Test Results
- **140 tests passed, 0 failed** (11 test files)

## Definition of Done Checklist
- [x] `vinyl-preview` is a valid preview mode in the designer store
- [x] It is the DEFAULT mode on page load
- [x] Vinyl button appears in the mode toolbar as the first option
- [x] Keyboard shortcut `v` works
- [x] Render API call uses `mode: 'vinyl-preview'` when selected
- [x] SVG preview area displays the dark-background vinyl SVG correctly (bg-[#111] background)
- [x] All existing tests pass
- [x] New tests pass
