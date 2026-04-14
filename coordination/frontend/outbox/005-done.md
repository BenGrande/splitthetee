# Task 005: Score-Keeping App — DONE

## What Was Implemented

### 1. Join Flow (JoinGame.vue)
- **Welcome screen**: "One Nine" branding + course name (from API)
- **Name entry**: Large input with "Join Game" button
- **API call**: `POST /api/v1/games/join` with `{ glass_set_id, player_name }`
- **Error handling**: Shows "Could not join game" on failure
- **Loading state**: Spinner during API call

### 2. Scorecard View (ScoreCard.vue)
- **Header**: App name, course name, hole progress (e.g., "Hole 7/18"), player name
- **Hole info card**: Current hole number, glass number, par, yardage, handicap, running cumulative score
- **Score buttons**: 7 large tap targets for -1 through +5 (relative to par)
  - Highlighted when that score is already recorded
  - Green flash animation on successful submission
  - Auto-advances to next unscored hole after scoring
- **+8 Penalty button**: Red/warning styled, for overshoots
- **Hole navigator**: Left/right arrows, centered hole display
- **Progress dots**: Bottom footer with 18 dots — filled for scored, outlined for unscored, enlarged for current
  - Tappable to jump to any hole
- **Optimistic updates**: Score saved locally immediately, API call in background
- **Score upsert**: Tapping different value on same hole changes the score

### 3. Leaderboard (Leaderboard.vue)
- **Sorted list**: Players sorted by total score (lowest wins)
- **Score display**: Relative to par (e.g., "+3", "-2", "E")
- **Medal icons**: Gold/silver/bronze for top 3
- **Current player highlight**: Border + "(you)" label
- **Stats**: Holes played count per player, current position
- **Auto-refresh**: Fetches `GET /api/v1/games/{session_id}/leaderboard` every 10 seconds
- **Back to Scorecard** button

### 4. State Management (stores/game.ts)
Full Pinia store with:
- **State**: glassSetId, glassNumber, sessionId, playerId, playerName, courseName, glassCount, holesPerGlass, holes, currentHole, scores, leaderboard, loading, connected, view
- **Computed**: totalHoles, currentHoleInfo, currentGlassNumber, cumulativeScore, holesScored
- **Actions**: joinGame, reconnect, submitScore, fetchLeaderboard, nextHole, prevHole, advanceToNextUnscored, saveToStorage, loadFromStorage

### 5. Reconnection via localStorage
- On mount, PlayView checks route params and attempts reconnect
- `saveToStorage()` stores sessionId/playerId/playerName keyed by glassSetId
- `reconnect()` loads from storage, validates session via `GET /api/v1/games/{sessionId}/status`
- Expired/invalid sessions cleared from storage, falls back to join flow

### 6. PlayView.vue (Orchestrator)
- Reads route params: `/play/:glassSetId?glass=N`
- Attempts reconnection on mount
- Switches between JoinGame, ScoreCard, Leaderboard based on `game.view`

### 7. Styling
- **Mobile-first**: Max-width containers, full-screen layout
- **Large touch targets**: Score buttons with py-4, 44px+ height
- **High contrast**: Dark emerald theme for outdoor visibility
- **No horizontal scrolling**
- **Smooth transitions**: Scale animations on score buttons, flash effects
- **One Nine branding** consistent with designer

### Files Created
- `src/stores/game.ts`
- `src/components/JoinGame.vue`
- `src/components/ScoreCard.vue`
- `src/components/Leaderboard.vue`
- `src/stores/__tests__/game.spec.ts` (26 tests)
- `src/components/__tests__/JoinGame.spec.ts` (7 tests)
- `src/components/__tests__/ScoreCard.spec.ts` (11 tests)
- `src/components/__tests__/Leaderboard.spec.ts` (6 tests)

### Files Modified
- `src/views/PlayView.vue` (replaced stub)

### Tests (128 total, 50 new)
Game store: 26 tests — defaults, computed properties, navigation, joinGame, submitScore, fetchLeaderboard, localStorage round-trip, reconnection
JoinGame: 7 tests — rendering, validation, API call, error display
ScoreCard: 11 tests — header, hole info, score buttons, penalty, navigator, progress dots, leaderboard link
Leaderboard: 6 tests — header, empty state, player display, current player highlight, auto-refresh note

### Deviations from Spec
- Dark theme is the only theme (no toggle) — appropriate for the emerald-themed app
- Pull-to-refresh not implemented (auto-refresh every 10s covers the use case)

## How to Test
1. `cd frontend && npm run dev`
2. Navigate to `/play/test-set-123?glass=1`
3. Enter name + click "Join Game" (requires API or shows error gracefully)
4. Scorecard: tap score buttons, verify highlight + auto-advance
5. Navigate holes with arrows, tap progress dots
6. Click "View Leaderboard" — see sorted scores
7. Leaderboard auto-refreshes every 10 seconds
8. Refresh page — reconnection via localStorage
9. Run `npx vitest run` — all 128 tests pass
