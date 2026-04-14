# Task 011: Debug + Fix Course Name Persistence on Reload (Issue 4)

**Priority**: Critical
**Depends on**: Nothing

**IMPORTANT**: Test the full flow end-to-end, not just the code structure.

---

## Problem
Course name disappears on page reload despite URL persistence code existing.

## Investigation Steps

### 1. Verify URL persistence
- In `DesignerView.vue`: confirm `router.replace()` is called with `courseId`, `lat`, `lng` after course selection
- Check: is the `router.replace()` actually executing? (Add `console.log` before it)
- Check: does `route.query` contain the params after selection?

### 2. Verify reload re-fetches course data
- In `DesignerView.vue` `onMounted()`: confirm it reads `route.query.lat`, `route.query.lng`, `route.query.courseId`
- Check: does it call the course data API with these params?
- Check: does the API response include `courseName`?
- Add `console.log('onMounted query:', route.query)` and `console.log('course data:', courseData)` for debugging

### 3. Verify render request includes course_name
- In `designer.ts` `buildRenderOptions()` or `renderPreview()`:
  - Check: is `course_name` included in the POST body to `/api/v1/render`?
  - Check: is `hole_range` (e.g., "Holes 1-6") computed and included?
  - Add logging: `console.log('render payload:', payload)` before the fetch call

### 4. Verify API reads and passes course_name
- Check `api/app/api/v1/render.py`: where does it read `course_name` from the request body?
- Does it pass it through to `render_svg()` in the options dict?
- This may need an API-side fix too — file a note for the API worker if so

## Required Fixes

### A. Ensure course_name flows through render pipeline
In `designer.ts` — `renderPreview()` or `buildRenderOptions()`:
```typescript
const payload = {
  ...buildRenderOptions(),
  course_name: courseStore.courseData?.courseName || '',
  hole_range: `Holes ${firstHole}-${lastHole}`,
  // ... other fields
}
```

### B. Compute and pass hole_range
- Determine which holes are on the current glass
- Format as "Holes X-Y" string
- Include in render options

### C. Ensure onMounted re-fetch restores full state
After course data is re-fetched on reload:
- Course store must be populated with `courseName`
- Designer store must trigger a re-render with the loaded course
- The SVG preview should auto-render once course data is available

## Files to Modify
| File | Changes |
|------|---------|
| `frontend/src/views/DesignerView.vue` | Debug URL persistence flow; ensure re-render after reload re-fetch |
| `frontend/src/stores/designer.ts` | Ensure course_name and hole_range in render payload |
| `frontend/src/stores/course.ts` | Verify courseName is populated from API response |

## Definition of Done
1. Select course → URL shows `?lat=X&lng=Y&courseId=Z`
2. Reload page → course data re-fetches automatically
3. After reload, glass preview renders with course name on left edge
4. "Holes X-Y" text visible below course name
5. Full cycle tested: search → select → verify name → reload → verify name persists
6. All tests pass
