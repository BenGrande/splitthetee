# Task 006: Phase 5 — Frontend Polish & Branding — DONE

## What Was Implemented

### 1. One Nine Branding
- **Logo**: Added `logo.png` to Search header and Designer header across all views
- **Favicon**: Updated `index.html` with PNG favicon from `logo.png`
- **Title**: Updated page title to "One Nine — Golf Glass Designer"
- **Consistent branding**: Logo + "One Nine" text in all view headers

### 2. Designer Polish

**Font hint integration:**
- `applyFontHint(courseData)` checks for `font_hint` in API response
- Auto-sets font selector to hinted font if match found in FONT_OPTIONS
- User can still override manually
- Called on course load (both from route params and search selection)

**Improved export naming (OnNine_ prefix):**
- SVG files: `OnNine_{CourseName}_Glass{N}_{Mode}.svg`
- ZIP files: `OnNine_{CourseName}_AllGlasses.zip`
- Cricut files: `OnNine_{CourseName}_Cricut_{layer}.svg`
- Cricut ZIP: `OnNine_{CourseName}_Cricut.zip`
- Settings files: `OnNine_{CourseName}_Settings.json`

**Print test layout:**
- `openPrintTest()` action opens a print-friendly page in new window
- Shows current glass SVG at 1:1 scale (or scaled to fit letter landscape)
- Includes 100mm reference ruler for scale verification
- Course name, glass number, scale %, and dimensions in header
- CSS `@page` for landscape, `@media print` to hide Print button
- "Print" button for user to trigger print dialog

**"Print Test" button** added to designer actions bar.

### 3. Score App Polish

**Undo support:**
- `lastScoredHole` tracks previous score state
- `undoLastScore()` reverts to previous value (or removes if new)
- Returns to the hole that was undone
- "Undo last score" button appears when undo is available

**Swipe gesture:**
- Touch start/end handlers on main content area
- Swipe right = previous hole, swipe left = next hole
- 60px threshold to avoid accidental swipes

**Haptic feedback:**
- `navigator.vibrate(30)` on score submission (if available)
- Graceful fallback when not supported

**Leaderboard share:**
- `shareLeaderboard()` formats leaderboard as text
- Copies to clipboard via `navigator.clipboard.writeText`
- "Share Leaderboard" button added below summary
- Includes medals, names, scores, and holes played

### 4. Accessibility
- `aria-label` on search input, hole navigation arrows, undo button, share button
- Proper semantic structure maintained

### 5. Build Verification
- `vue-tsc --noEmit` passes with zero errors
- `npm run build` succeeds — production bundle generated
- Fixed `vite.config.ts` — added `/// <reference types="vitest/config" />` for test config compatibility
- Cleaned up unused imports/variables across all files

### Files Modified
- `index.html` — favicon, title
- `vite.config.ts` — vitest config reference
- `src/views/SearchView.vue` — logo, aria-label
- `src/views/DesignerView.vue` — logo, font hint, print test button
- `src/views/__tests__/SearchView.spec.ts` — unused var fix
- `src/stores/designer.ts` — applyFontHint, openPrintTest, OnNine_ naming, unused import fix
- `src/stores/game.ts` — undoLastScore, shareLeaderboard, lastScoredHole
- `src/components/ScoreCard.vue` — undo button, swipe, haptic, aria-labels
- `src/components/Leaderboard.vue` — share button
- `src/components/SvgPreview.vue` — unused ref fix
- `src/stores/__tests__/designer.spec.ts` — font hint tests, unused var fix
- `src/stores/__tests__/game.spec.ts` — undo/share tests

### Tests (135 total, 7 new)
New tests:
- `applyFontHint sets font when match found`
- `applyFontHint does nothing with no hint`
- `applyFontHint ignores unknown font`
- `undoLastScore reverts the last score`
- `undoLastScore does nothing when no last score`
- `shareLeaderboard returns formatted text`
- `shareLeaderboard returns empty string when no entries`

### Build Output
```
dist/index.html                    0.70 kB
dist/assets/index.css             31.47 kB (gzip: 6.34 kB)
dist/assets/SearchView.js          7.87 kB (gzip: 2.88 kB)
dist/assets/PlayView.js           13.92 kB (gzip: 4.79 kB)
dist/assets/DesignerView.js       35.23 kB (gzip: 10.35 kB)
```

### Deviations from Spec
- Glass template info panel (cross-section SVG) deferred — would add complexity; glass info is shown in header tooltip
- Full navigation bar deferred — each view has its own header with logo/back links which works well for the 3-view app
- Expandable leaderboard rows deferred — would need per-player hole-by-hole data from API
- Lazy loading already in place via Vue Router's dynamic imports

## How to Test
1. `npm run build` — verify clean build
2. `npx vitest run` — all 135 tests pass
3. `npm run dev` — verify logo in Search + Designer headers
4. Designer: load course → verify font auto-applied if API returns `font_hint`
5. Designer: click "Print Test" → verify 1:1 print page opens
6. Export SVG → verify `OnNine_` prefix in filename
7. Score app: submit score → feel haptic buzz (on mobile), see undo button
8. Score app: swipe left/right → hole navigation
9. Leaderboard: click "Share Leaderboard" → text copied to clipboard
