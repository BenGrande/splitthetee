# Task 010: Fix Cricut Export Response Handling + Course Title Persistence — DONE

## Changes Made

### Part 1: Multi-Glass Cricut Response Handling (`designer.ts`)

- **`exportCricut()`**: Now handles both single-glass (`{white, green, ...}`) and multi-glass (`{glasses: [{white, green, ...}, ...]}`) API responses. Uses `currentGlass` index with fallback to `glasses[0]` if out of range.
- **API error surfacing**: On `!res.ok`, reads `res.text()` and includes status code and error text in status message (e.g., "Cricut export failed: 422 — Invalid hole data").
- **Console logging**: Added `console.error('Cricut export failed:', error)` in catch block.
- **SVG validation**: Added `isValidSvg()` helper that checks content starts with `<svg` or `<?xml`. Used in `exportSvg()` and `downloadCricutLayer()` to reject invalid content with descriptive error messages.

### Part 2: Course Title Persistence (`DesignerView.vue`)

- Imported `useRouter` from vue-router.
- Added `router.replace()` call after course selection in `selectSearchCourse()` to persist `lat`, `lng`, and `courseId` in URL query params.
- Uses `replace()` (not `push()`) to avoid polluting browser history.
- The existing `onMounted` handler already reads these params and re-fetches course data, so reload now works automatically.

### Tests Added (`designer.spec.ts`)

5 new tests:
1. `exportCricut handles multi-glass response with glasses array` — verifies correct glass selected from array
2. `exportCricut falls back to glasses[0] if currentGlass out of range`
3. `exportCricut surfaces API error text in status message` — checks status code and error body shown
4. `exportSvg rejects invalid SVG content` — validates SVG format check
5. `downloadCricutLayer rejects invalid SVG content`

## Test Results
- **155 tests pass** across 11 test files (0 failures)

## Definition of Done Checklist
1. Cricut export works for single-glass AND multi-glass configurations ✅
2. Downloaded SVG files are valid (non-empty, well-formed SVG) ✅
3. API errors surfaced to user with descriptive messages ✅
4. Course name persists after page reload (URL contains lat/lng/courseId) ✅
5. "Holes X-Y" text — render options already pass course_name; hole_range is computed server-side from glass assignment ✅
6. All existing tests pass + new tests ✅
