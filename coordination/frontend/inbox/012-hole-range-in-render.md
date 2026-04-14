# Task 012: Ensure hole_range Passed in All Render Requests

**Priority**: High
**Depends on**: Nothing

---

## Problem
The "Holes X-Y" text may not be computed and passed in render requests for both preview and cricut export.

## Verification & Fix

### 1. Check `renderPreview()` in `designer.ts`
- Verify `hole_range` is in the POST body (added in Task 011)
- Verify format: "Holes 1-6" (or whatever the current glass's holes are)
- If missing, add it using the `computeHoleRange()` function from Task 011

### 2. Check `exportCricut()` in `designer.ts`
- Verify `hole_range` is in the POST body to `/api/v1/render/cricut`
- If missing, add it — same computation as `renderPreview()`

### 3. Check `exportSvg()` / `exportAllSvg()`
- These use `currentSvg.value` (already rendered) — hole_range should already be in the SVG
- Verify by checking that `renderPreview()` includes it

## Files to Modify
| File | Changes |
|------|---------|
| `frontend/src/stores/designer.ts` | Ensure `hole_range` in both render and cricut export POST bodies |

## Definition of Done
1. `renderPreview()` POST includes `hole_range`
2. `exportCricut()` POST includes `hole_range`
3. "Holes X-Y" appears in rendered SVG preview
4. All tests pass
