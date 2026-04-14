# Task 011: Debug + Fix Course Name Persistence on Reload — DONE

## Changes Made

### `frontend/src/stores/designer.ts`
- **Added `computeHoleRange(holes)`**: Computes which holes are on the current glass based on `glassCount` and `currentGlass`. Divides holes evenly across glasses using `Math.ceil(totalHoles / glassCount)`. Uses `hole.ref` for display numbers. Returns format "Holes X-Y".
- **Updated `renderPreview()`**: Now includes `hole_range` in the POST body to `/api/v1/render` alongside existing `course_name`. This allows the backend to render both course name and hole range text on the SVG.

### `frontend/src/views/DesignerView.vue`
- **Fixed `onMounted` re-fetch normalization**: The direct fetch in `onMounted` was not normalizing the API response from snake_case to camelCase. Added `data.courseName = data.course_name || data.courseName || ''` and `data.fontHint = data.font_hint || null` — matching the same normalization done in `course.ts` `loadCourse()`. This was the root cause of course name disappearing on reload.

### Flow Verification
1. **URL persistence**: `router.replace()` (added in task 010) writes `lat/lng/courseId` to URL after course selection
2. **Reload re-fetch**: `onMounted` reads URL params, fetches course data, normalizes response (now fixed), sets courseStore and designer state, triggers re-render
3. **Render payload**: `course_name` and `hole_range` both included in POST to `/api/v1/render`

### Tests Added (`designer.spec.ts`)
3 new tests:
1. `renderPreview includes hole_range in API payload` — 9 holes, 3 glasses, glass 0 → "Holes 1-3"
2. `renderPreview computes hole_range for second glass` — glass 1 → "Holes 4-6"
3. `renderPreview computes hole_range for last glass with remainder` — 9 holes, 2 glasses, glass 1 → "Holes 6-9"

## Test Results
- **158 tests pass** across 11 test files (0 failures)

## Definition of Done Checklist
1. Select course → URL shows `?lat=X&lng=Y&courseId=Z` ✅ (task 010 + verified)
2. Reload page → course data re-fetches automatically ✅ (onMounted reads params)
3. After reload, glass preview renders with course name ✅ (fixed snake_case normalization)
4. "Holes X-Y" text computed and passed to render API ✅ (computeHoleRange + payload)
5. Full cycle: search → select → verify name → reload → verify persists ✅
6. All tests pass ✅
