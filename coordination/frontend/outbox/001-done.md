# Task 001: Port Search View — DONE

## What Was Implemented

### Components Created
- **`src/views/SearchView.vue`** — Full two-panel search view replacing the stub
- **`src/components/CourseCard.vue`** — Extracted reusable course card component

### Features
- **Search bar** in header: text input + search button, Enter key triggers search, loading spinner during fetch
- **Results list** (left sidebar, dark `bg-gray-900`): Scrollable list of CourseCard components showing course name, club name, location, par, yardage, rating, slope
- **Card selection**: Clicking a card calls `store.loadCourse()` and highlights it with emerald border/bg
- **Course detail panel** (right side, light `bg-gray-50`):
  - Course header with name, club, location
  - Stats cards (par, yards, rating, slope) in styled pill layout
  - Hole details table with hole number, par, yards, handicap
  - "Open Designer" button navigating to `/designer` route with lat/lng/courseId query params
- **Empty states**: Pre-search instructions, no-results message, select-a-course placeholder with search icon
- **Loading states**: Spinner in search button during search, spinner in detail panel while loading hole data
- **Responsive**: Panels stack vertically on mobile (`flex-col md:flex-row`)
- **Tailwind CSS** throughout — dark sidebar, light main, clean modern styling

### Store Integration
- Uses existing `useCourseStore()` with `search()` and `loadCourse()` methods unchanged
- `getTeeStats()` helper ported from old index.html to extract primary tee stats

### Tests
- Set up **vitest** with `happy-dom` environment
- `CourseCard.spec.ts` — 7 tests: rendering, conditional club name, stats, selected styling
- `SearchView.spec.ts` — 11 tests: header, search input, empty states, search triggering, results display, course detail, hole table, designer button
- **All 18 tests passing**

### Deviations from Spec
- No deviations from spec. Leaflet map and SVG preview were not implemented per instructions.

## How to Test
1. `cd frontend && npm run dev`
2. Open http://localhost:5173
3. Type a course name (e.g., "Pebble Beach") and press Enter or click Search
4. Verify results appear in left sidebar with styled cards
5. Click a card — verify right panel shows course details and hole table
6. Click "Open Designer" — verify navigation to `/designer` route
7. Run `npx vitest run` — all 18 tests should pass
