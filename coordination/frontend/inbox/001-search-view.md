# Task 001: Port Search View from index.html to Vue

## Priority: HIGH — first user-facing feature

## What to Build

Port the search/course-selection UI from the old `public/index.html` into the Vue `SearchView.vue`. This is the landing page of the app.

### Layout (reference old index.html)

**Two-panel layout:**
- **Left sidebar** (~380px): Search input + results list
- **Right main area**: Course details / map placeholder

### Search Panel (left sidebar)
1. **Search bar**: Text input + search button at top
   - Enter key triggers search
   - Loading spinner during fetch
2. **Results list**: Scrollable list of course cards
   - Each card shows: course name (bold), club name, location (city, state), par, yardage
   - Click a card to select it (highlight with border/bg change)
3. **Empty state**: "Search for a golf course to get started" when no results

### Course Detail Panel (right side)
When a course is selected:
1. **Course header**: Name, club, location, par/yardage/rating/slope
2. **Hole table**: Simple table or grid showing all 18 holes with par, yardage, handicap
3. **Action buttons**:
   - "Open Designer" — navigates to `/designer` route (pass course data via store or query params)

When no course selected:
- Show a placeholder/empty state with instructions

### Store Integration
The `stores/course.ts` already has `search(query)` and `loadCourse(course)` methods. Use them.
- `search()` calls `GET /api/v1/search?q=...`
- `loadCourse()` calls `GET /api/v1/course-holes?lat=...&lng=...&courseId=...`

### Styling
- Use Tailwind CSS utility classes
- Dark sidebar (`bg-gray-900 text-white`), light main area (`bg-gray-50`)
- Responsive: on mobile, stack panels vertically
- Clean, modern look — this is a premium product

### DO NOT implement:
- Leaflet map integration (defer to later task)
- SVG course preview (that's the designer)
- Any modifications to API endpoints

## Reference Files (READ ONLY)
- `/Users/contextuallabs/code/one-nine/public/index.html` — old search UI to port from
- `/Users/contextuallabs/code/one-nine/frontend/src/stores/course.ts` — existing store

## Files to Modify
- MODIFY: `frontend/src/views/SearchView.vue` (replace stub)
- CREATE: `frontend/src/components/CourseCard.vue` (optional — extract if needed)
- MODIFY: `frontend/src/stores/course.ts` if needed (add types, selectedCourse handling)

## Definition of Done
- [ ] Search bar works — typing + Enter or click triggers search
- [ ] Results display as styled cards with course info
- [ ] Clicking a card selects it and shows details in right panel
- [ ] "Open Designer" button navigates to `/designer`
- [ ] Responsive layout (mobile stacks vertically)
- [ ] Loading states shown during API calls
- [ ] No console errors

## Done Report
When complete, write your done report to: `coordination/frontend/outbox/001-done.md`
Include: what was implemented, components created, any deviations from spec, how to test.
