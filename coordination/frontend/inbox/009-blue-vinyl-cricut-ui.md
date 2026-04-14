# Task 009: Add Blue Vinyl Layer to Cricut Export UI

**Priority**: High
**Depends on**: API Task 012 (blue vinyl backend)

---

## Overview
The API now has a blue vinyl layer for water hazards. The frontend Cricut export panel needs to support it.

## Changes Required

### 1. `CricutExportPanel.vue`
- Add "Blue (Water)" layer to the list of exportable cricut layers
- Button to download blue layer individually
- Blue layer included in "Download All Layers" ZIP
- Visual indicator: blue color swatch next to the layer name

### 2. `designer.ts` Store
- Update cricut export state to include `blue` layer alongside `white`, `green`, `tan`
- Update `exportCricut()` to expect `blue` in the API response
- Update `downloadCricutLayer('blue')` to handle the blue layer
- Update `downloadAllCricutLayers()` to include blue in the ZIP

### 3. Layer Label/Description
- White: "Outlines, labels, ruler, zones, scores"
- Blue: "Water hazards"
- Green: "Greens, tees, fairway accents"
- Tan: "Bunkers"

## Files to Modify
| File | Changes |
|------|---------|
| `frontend/src/stores/designer.ts` | Add `blue` to cricut layer state and export functions |
| `frontend/src/components/CricutExportPanel.vue` | Add blue layer button, include in ZIP, show blue swatch |

## Definition of Done
1. Blue layer appears in Cricut export panel with blue color indicator
2. "Download Blue" button downloads the blue water hazard SVG
3. "Download All" ZIP includes blue layer alongside white/green/tan
4. Blue layer label says "Water hazards"
5. All existing tests pass + new tests for blue layer UI
