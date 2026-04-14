# Task 006: Phase 5 — Frontend Polish & Branding

## Priority: MEDIUM — final polish pass

## What to Build

### 1. One Nine Branding

**Logo integration:**
- Add One Nine logo to app header/nav (all views)
- Logo source: fetch from `GET /api/v1/assets/logo` or use a local copy
- Small logo in nav bar (left side), text "One Nine" next to it
- Consistent branding across Search, Designer, and Play views

**Favicon:**
- If `public/logo.png` exists in project root, copy/convert for use as favicon
- Update `index.html` with proper favicon link

### 2. Designer Polish

**Font hint integration:**
- When loading course data, check for `font_hint` in API response
- If present, auto-set the font selector to the hinted font
- User can still override manually

**Glass template info panel:**
- Expandable panel showing computed glass geometry:
  - Volume (ml), circumference, slant height
  - Visual cross-section diagram (simple SVG)
- Positioned in left sidebar below glass dimensions

**Improved export naming:**
- SVG files: `OnNine_{CourseName}_Glass{N}_{Mode}.svg`
- ZIP files: `OnNine_{CourseName}_Cricut.zip`
- Settings files: `OnNine_{CourseName}_Settings.json`

**Print test layout:**
- "Print Test" button that opens a print-friendly page
- Shows the current glass SVG at 1:1 scale
- Includes the 10mm reference bar prominently
- CSS `@media print` styles for clean printing

### 3. Score App Polish

**Enhanced join screen:**
- Show glass number and course info before joining
- Show existing players if session is active ("Mike and 2 others are playing")
- Animate the transition from join to scorecard

**Scorecard improvements:**
- Swipe gesture for hole navigation (left/right swipe)
- Haptic feedback on score submission (if navigator.vibrate available)
- Score history: small summary showing last 3 scored holes
- "Undo" button for last score (reverts to previous or clears)

**Leaderboard improvements:**
- Expandable player rows showing per-hole breakdown
- Score relative to course par (not just individual scores)
- Front 9 / Back 9 subtotals
- "Share" button — copies leaderboard text to clipboard

### 4. Navigation & Routing

- Add a proper navigation bar across all views:
  - Logo + "One Nine" (links to home/search)
  - "Designer" link (if course loaded)
  - "Score" link (if in a game)
- Active route highlighted
- Mobile: hamburger menu or bottom tab bar

### 5. Error & Empty States

Audit all views for proper error and empty states:
- **Search**: No results found for query
- **Designer**: No course loaded (prompt to search first)
- **Play**: Invalid glass set ID, session expired, API unavailable
- All errors should be user-friendly, not raw API messages

### 6. Accessibility & Performance

- Proper `aria-label` attributes on interactive elements
- Focus management (trap focus in modals)
- Color contrast check (especially on dark theme)
- Lazy load heavy components (CricutExportPanel, Leaderboard)
- Debounce search input (already done, verify)

### 7. Build Verification

- Run `npm run build` and verify production build succeeds
- Check for TypeScript errors with `vue-tsc --noEmit`
- Verify all routes work in production build (hash vs history mode)
- Update `vite.config.ts` if needed for production API proxy

## Files to Modify
- MODIFY: `frontend/src/App.vue` (add navigation bar)
- MODIFY: `frontend/src/views/SearchView.vue` (branding, error states)
- MODIFY: `frontend/src/views/DesignerView.vue` (font hints, print test, export naming, glass info panel)
- MODIFY: `frontend/src/views/PlayView.vue` (enhanced join, swipe, share)
- MODIFY: `frontend/src/stores/designer.ts` (font hint auto-set, export naming)
- MODIFY: `frontend/src/stores/game.ts` (undo, swipe)
- MODIFY: `frontend/src/components/ScoreCard.vue` (swipe, haptic, undo)
- MODIFY: `frontend/src/components/Leaderboard.vue` (expandable rows, share, subtotals)
- MODIFY: `frontend/src/components/JoinGame.vue` (player count, animations)
- MODIFY: `frontend/index.html` (favicon)

## Definition of Done
- [ ] One Nine logo in nav bar across all views
- [ ] Font hint auto-applied in designer when available
- [ ] Export files named with "OnNine_" prefix
- [ ] Print test page works at 1:1 scale
- [ ] Score app join shows existing players
- [ ] Leaderboard has expandable rows + share button
- [ ] Navigation bar with active route highlighting
- [ ] Error states audited and user-friendly
- [ ] Aria labels on key interactive elements
- [ ] `npm run build` succeeds without errors
- [ ] `vue-tsc --noEmit` passes

## Done Report
When complete, write your done report to: `coordination/frontend/outbox/006-done.md`
