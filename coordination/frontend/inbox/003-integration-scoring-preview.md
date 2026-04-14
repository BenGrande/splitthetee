# Task 003: End-to-End Integration + Scoring Preview Controls (Phase 2)

## Priority: HIGH — connect designer to real API + add scoring preview

## Prerequisites
- Frontend Tasks 001-002 complete (search + designer views)
- API Tasks 001-003 complete (all endpoints working)

## What to Build

### 1. End-to-End Integration Testing & Fixes

The designer currently has API fallback logic (placeholder SVG when API unavailable). Now that the API is fully implemented, verify and fix the integration:

**Search → Course Selection → Designer flow:**
1. Search works and returns real courses
2. Selecting a course loads hole data via `loadCourse()`
3. "Open Designer" passes lat/lng/courseId to designer route
4. Designer loads course data from route params on mount
5. Designer calls `POST /api/v1/render` with real hole data
6. SVG preview displays the actual course layout
7. Switching glass count (1/2/3/6) re-renders with correct splits
8. Glass mode vs rect mode toggle works
9. Layer toggles affect the rendered SVG
10. Style changes trigger re-render with updated colors

**Fix any issues found** in the integration. Common problems to check:
- Data shape mismatches between frontend expectations and API responses
- CORS issues (should be configured already)
- Missing error handling for specific API error shapes
- Course data not being passed correctly between views

### 2. Settings Save/Load Integration

Verify settings CRUD works end-to-end:
1. "Save Settings" calls `POST /api/v1/settings` with current designer state
2. Verify saved settings appear in load list
3. Loading a saved setting restores all controls (glass count, dimensions, styles, layers, font)
4. Add a **"Load Settings" modal/dropdown** if not already implemented:
   - Lists saved configs from `GET /api/v1/settings`
   - Shows course name + saved date
   - Click to load and apply

### 3. Scoring Preview Mode Toggle

Add a new preview mode option in the designer:

**In GlassControls.vue or DesignerView.vue:**
- Add "Scoring Preview" as a third preview mode option alongside "Glass" and "Rect"
- When selected, calls `POST /api/v1/render` with `mode: "scoring-preview"`
- This mode shows colored scoring zone bands overlaid on the layout
- Useful for visualizing where scoring zones fall relative to greens

**In the designer store:**
- Update `previewMode` to accept `'glass' | 'rect' | 'scoring-preview'`
- Pass mode to render API call

### 4. Ruler Toggle

Add a "Show Ruler" toggle to LayerControls:
- New layer: "ruler" — toggleable in the layer system
- When enabled, the render API includes the ruler on the right edge
- Pass in `hidden_layers` to the render API call

### 5. Export Improvements

**Single SVG export** should work reliably:
- Download the currently displayed SVG as a `.svg` file
- Filename format: `{courseName}_glass{N}_{mode}.svg`

**Multi-glass export** (if possible):
- If a ZIP library is available (`jszip` or similar), add it and implement "Export All"
- Downloads a ZIP with one SVG per glass
- If no ZIP library, add `jszip` to package.json dependencies

### 6. Polish & UX

- Add course name display in designer header
- Show glass template info (volume, dimensions) in a tooltip or info panel
- Keyboard shortcuts: `1-6` keys to switch glass count, `g/r/s` for preview mode
- Loading states during render (spinner/overlay on preview)

## Reference
- API endpoints (all should be working now):
  - `GET /api/v1/search?q=...`
  - `GET /api/v1/course-holes?lat=...&lng=...&courseId=...`
  - `POST /api/v1/render` — `{ holes, options: { mode, glass_count, styles, hidden_layers, ... } }`
  - `POST /api/v1/render/glass-template` — `{ glass_height, top_radius, ... }`
  - `POST /api/v1/settings` — `{ course_name, settings }`
  - `GET /api/v1/settings` — list
  - `GET /api/v1/settings/:id` — load

## Files to Modify
- MODIFY: `frontend/src/views/DesignerView.vue` (integration fixes, course name display, keyboard shortcuts)
- MODIFY: `frontend/src/stores/designer.ts` (scoring-preview mode, render API payload fixes)
- MODIFY: `frontend/src/stores/course.ts` (any data shape fixes needed)
- MODIFY: `frontend/src/components/GlassControls.vue` (scoring preview mode option)
- MODIFY: `frontend/src/components/LayerControls.vue` (ruler toggle)
- MODIFY: `frontend/src/components/SvgPreview.vue` (any rendering fixes)
- POSSIBLY ADD: `jszip` dependency for multi-glass export

## Definition of Done
- [ ] Full flow works: search → select course → open designer → see real SVG preview
- [ ] Changing glass count, mode, layers, styles triggers correct re-renders
- [ ] Settings save/load works end-to-end with API
- [ ] Scoring preview mode shows colored zone bands
- [ ] Ruler toggle works
- [ ] Single SVG export downloads correctly named file
- [ ] Course name shown in designer header
- [ ] No console errors during normal usage

## Done Report
When complete, write your done report to: `coordination/frontend/outbox/003-done.md`
