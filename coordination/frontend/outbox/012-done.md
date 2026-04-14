# Task 012: Ensure hole_range Passed in All Render Requests — DONE

## Changes Made

### `frontend/src/stores/designer.ts`
- **`exportCricut()`**: Added `hole_range` to the POST body sent to `/api/v1/render/cricut`. Uses the same `computeHoleRange()` function already added in Task 011.

### Verification
- **`renderPreview()`**: Already includes `hole_range` in POST body (added in Task 011) ✅
- **`exportCricut()`**: Now includes `hole_range` in POST body ✅
- **`exportSvg()` / `exportAllSvg()`**: Use already-rendered `svgContent` which includes hole_range from the render call ✅

### Tests Added (`designer.spec.ts`)
1. `exportCricut includes hole_range in API payload` — verifies hole_range and course_name in cricut export POST body

## Test Results
- **159 tests pass** across 11 test files (0 failures)

## Definition of Done Checklist
1. `renderPreview()` POST includes `hole_range` ✅
2. `exportCricut()` POST includes `hole_range` ✅
3. "Holes X-Y" available for rendered SVG preview ✅
4. All tests pass ✅
