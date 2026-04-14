# Task 008: Fix Export Functionality (SVG + ZIP Downloads)

**Priority**: Critical — users can't export anything
**Depends on**: API Task 011 (export endpoints verified)

---

## Problem
Both SVG and ZIP downloads produce empty/corrupt files. The download triggers but the resulting files are unusable.

## Export Flows to Fix

### 1. Single SVG Export (`exportSvg()` in `designer.ts`)
- Creates blob from `currentSvg.value` and triggers download via `<a>` tag
- **Check**: Is `currentSvg.value` populated when export is triggered?
- **Check**: Is the blob MIME type correct (`image/svg+xml`)?
- **Check**: Is the `<a>` tag download attribute set correctly?
- **Fix**: Add guard — if `currentSvg.value` is empty/null, show error toast instead of downloading empty file

### 2. All SVGs ZIP Export (`exportAllSvg()` in `designer.ts`)
- Loops through glasses, renders each, zips into a single file
- **Check**: Is JSZip imported and working?
- **Check**: Is `generateAsync()` properly awaited?
- **Check**: Are the individual glass SVGs actually rendered before zipping?
- **Fix**: Add error handling at each step; show progress or error feedback

### 3. Cricut Export (`exportCricut()` in `designer.ts`)
- POSTs to `/api/v1/render/cricut`
- **Check**: Is the POST body correct (same shape as render endpoint)?
- **Check**: Is the response parsed correctly (JSON with `white`, `green`, `tan` SVG strings)?
- **Check**: Are the response SVGs stored in the right reactive state?
- **Fix**: Add try/catch, check response.ok, surface errors to user

### 4. Cricut Layer Downloads (`downloadCricutLayer()` / `downloadAllCricutLayers()`)
- Downloads individual or zipped cricut layers from stored state
- **Check**: Is the stored cricut data available when download is triggered?
- **Fix**: Guard against empty data, show error if layers not yet generated

## Error UX
- When an export fails, show a visible error message (toast or inline) — don't silently produce an empty file
- Disable export buttons when there's no SVG content to export
- Show loading state during ZIP generation and cricut API call

## Files to Modify
| File | Changes |
|------|---------|
| `frontend/src/stores/designer.ts` | Fix all export functions: add guards for empty content, proper error handling, verify blob creation, verify JSZip usage |
| `frontend/src/components/CricutExportPanel.vue` | Disable buttons when no content; show errors; loading states |
| `frontend/src/views/DesignerView.vue` | Disable SVG export buttons when currentSvg is empty |

## Definition of Done
1. Single SVG download produces a valid `.svg` file that opens in a browser/Inkscape
2. All SVGs ZIP download produces a valid `.zip` with one SVG per glass
3. Cricut export calls the API and stores the response layers
4. Cricut single layer download produces a valid `.svg` file
5. Cricut all layers ZIP download produces a valid `.zip` with white/green/tan SVGs
6. Error messages shown when export fails (not silent empty files)
7. Export buttons disabled when no content available
8. All existing tests pass + new tests for export error handling
