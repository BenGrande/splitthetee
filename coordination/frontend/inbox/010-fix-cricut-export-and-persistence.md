# Task 010: Fix Cricut Export Response Handling + Course Title Persistence

**Priority**: Critical
**Depends on**: API Task 016

---

## Part 1: Fix Multi-Glass Cricut Response Handling

### Problem
When `glass_count > 1`, the API returns `{"glasses": [{white, green, ...}, ...]}` but the frontend parses `data.white` directly — which is `undefined` for multi-glass responses.

### Fix in `designer.ts` — `exportCricut()`
```typescript
const data = await res.json()
if (data.glasses) {
  // Multi-glass: use the current glass index
  cricutSvgs.value = data.glasses[currentGlass.value] || data.glasses[0]
} else {
  // Single glass: response is directly {white, green, tan, blue, guide}
  cricutSvgs.value = data
}
```

### Additional Export Fixes
- **Log full errors**: `console.error('Cricut export failed:', error)` in catch blocks
- **Surface API errors**: If `!res.ok`, read `res.text()` and show in status message
- **Validate SVG content before download**: Check that SVG string is non-empty and starts with `<svg` or `<?xml` before creating blob. Show error if invalid.

## Part 2: Course Title Persistence via URL Params

### Problem
Course name and "Holes X-Y" disappear on page reload because course data is in-memory only (Pinia resets).

### Fix in `DesignerView.vue`
After a course is selected and hole data loaded, update the URL:
```typescript
router.replace({
  query: {
    lat: courseStore.courseData.lat,
    lng: courseStore.courseData.lng,
    courseId: courseStore.courseData.id
  }
})
```
Use `router.replace()` (not `push()`) to avoid polluting history.

The existing `onMounted` already checks `route.query.lat/lng/courseId` and re-fetches — this just needs the params to be in the URL.

### Fix in `designer.ts` — `buildRenderOptions()`
Ensure the render options include:
- `course_name`: from `courseStore.courseData.courseName` (or equivalent field)
- `hole_range`: computed from holes on the current glass (e.g., "Holes 1-6")

Verify these are passed to the API and the backend actually uses them in SVG rendering.

## Files to Modify
| File | Changes |
|------|---------|
| `frontend/src/stores/designer.ts` | Fix multi-glass response handling; validate SVG before download; ensure course_name and hole_range in render options |
| `frontend/src/views/DesignerView.vue` | Add `router.replace()` after course selection to persist params in URL |
| `frontend/src/stores/course.ts` | Optional: expose courseId for easy access |

## Definition of Done
1. Cricut export works for single-glass AND multi-glass configurations
2. Downloaded SVG files are valid (non-empty, well-formed SVG)
3. API errors surfaced to user with descriptive messages
4. Course name persists after page reload (URL contains lat/lng/courseId)
5. "Holes X-Y" text rendered on glass preview
6. All existing tests pass + new tests
