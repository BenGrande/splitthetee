# Task 005: Score-Keeping App (Phase 4)

## Priority: MEDIUM — independent from designer

## Prerequisites
- Router already has `/play/:glassSetId` route pointing to PlayView.vue
- Score-keeping API endpoints may not be ready yet — design to degrade gracefully

## What to Build

Port the score-keeping app into PlayView.vue. This is a **mobile-first** web app opened via QR code scan on the physical glass.

### 1. Join Flow

When user opens `/play/{glassSetId}?glass={glassNumber}`:

1. **Welcome screen**: Show "One Nine" branding + course name (fetched from glass set)
2. **Name entry**: Simple input "Enter your name" + "Join Game" button
3. Call `POST /api/v1/games/join` with `{ glass_set_id, player_name }`
4. On success, transition to scorecard view
5. Store `session_id` and `player_id` in localStorage for reconnection

**Reconnection**: If user refreshes or returns:
- Check localStorage for existing session/player for this glass set
- If found, skip name entry and go straight to scorecard
- Validate session is still active via API

### 2. Scorecard View

Main view after joining — shows current round progress.

**Layout (mobile-first, full-screen):**
```
┌─────────────────────────┐
│ One Nine    Hole 7/18   │  ← header with progress
│ Pebble Beach            │  ← course name
├─────────────────────────┤
│                         │
│   ┌─────────────────┐   │
│   │   Glass 2       │   │  ← current glass indicator
│   │   Hole 7        │   │
│   │   Par 4 · 385yd │   │  ← hole info
│   └─────────────────┘   │
│                         │
│   Your Score:           │
│   ┌──┬──┬──┬──┬──┬──┬──┐│
│   │-1│ 0│ 1│ 2│ 3│ 4│ 5││  ← tap to score
│   └──┴──┴──┴──┴──┴──┴──┘│
│        [+8 Penalty]     │  ← overshoot button
│                         │
│   ┌─────────────────┐   │
│   │  ◀  Hole 7  ▶   │   │  ← hole navigator
│   └─────────────────┘   │
│                         │
│   [View Leaderboard]    │  ← link to leaderboard
│                         │
├─────────────────────────┤
│ ● ● ● ○ ○ ○            │  ← hole progress dots
└─────────────────────────┘
```

**Score entry:**
- Large tap targets for each score (-1, 0, 1, 2, 3, 4, 5)
- Separate "+8 Penalty" button for overshoots (styled differently — red/warning)
- Tapping a score submits immediately via `POST /api/v1/games/{session_id}/score`
- Visual confirmation (green flash/check) on successful submission
- Already-scored holes show the recorded score (highlighted button)
- Can change score by tapping different value (upsert)

**Hole navigation:**
- Left/right arrows to move between holes
- Progress dots at bottom showing scored vs unscored holes
- Auto-advance to next unscored hole after scoring
- Glass number auto-calculated from hole number and holes_per_glass

**Hole info display:**
- Current hole number, par, yardage, handicap
- Glass number
- Cumulative score so far

### 3. Leaderboard View

Accessible from scorecard via "View Leaderboard" button.

**Layout:**
```
┌─────────────────────────┐
│ Leaderboard             │
│ Pebble Beach            │
├─────────────────────────┤
│ 🥇 1. Mike      -2     │  ← sorted by total (lowest wins)
│ 🥈 2. Sarah     +3     │
│ 🥉 3. Tom       +7     │
│    4. Lisa      +12    │
├─────────────────────────┤
│ Holes: 14/18            │
│ Your position: 2nd      │
│                         │
│ [Back to Scorecard]     │
└─────────────────────────┘
```

**Features:**
- Fetches from `GET /api/v1/games/{session_id}/leaderboard`
- Auto-refresh every 10 seconds (or pull-to-refresh)
- Highlights current player's row
- Shows cumulative scores relative to par (e.g., "+3" or "-2")
- Medal icons for top 3
- Holes played count per player

### 4. State Management

Create `frontend/src/stores/game.ts`:

```typescript
{
  glassSetId: string
  glassNumber: number
  sessionId: string | null
  playerId: string | null
  playerName: string
  courseName: string
  glassCount: number
  holesPerGlass: number
  totalHoles: number  // computed: glassCount * holesPerGlass
  currentHole: number
  scores: Map<number, number>  // hole_number -> score
  leaderboard: LeaderboardEntry[]
  loading: boolean
  connected: boolean
}
```

Actions:
- `joinGame(glassSetId, playerName)` — POST join, store IDs
- `submitScore(holeNumber, score)` — POST score, update local state
- `fetchLeaderboard()` — GET leaderboard
- `nextHole()` / `prevHole()` — navigate holes
- `reconnect()` — check localStorage, validate session

### 5. Styling

- **Mobile-first**: designed for phone screens (max-width ~430px typical)
- Large touch targets (min 44px height for score buttons)
- High contrast for outdoor visibility
- Dark theme option (beer in sunlight context)
- Smooth transitions between views
- No horizontal scrolling
- One Nine branding consistent with designer

## Files to Create/Modify
- MODIFY: `frontend/src/views/PlayView.vue` (replace stub)
- CREATE: `frontend/src/stores/game.ts`
- CREATE: `frontend/src/components/ScoreCard.vue` (score entry + hole nav)
- CREATE: `frontend/src/components/Leaderboard.vue` (leaderboard display)
- CREATE: `frontend/src/components/JoinGame.vue` (name entry flow)

## Definition of Done
- [ ] QR scan URL opens join flow with course name
- [ ] Name entry + "Join Game" works (or graceful fallback)
- [ ] Scorecard shows current hole with par/yardage info
- [ ] Score buttons (-1 through 5 + penalty) submit scores
- [ ] Hole navigation (prev/next) works with progress dots
- [ ] Leaderboard shows sorted cumulative scores
- [ ] Auto-refresh leaderboard every 10 seconds
- [ ] Current player highlighted in leaderboard
- [ ] localStorage reconnection works
- [ ] Mobile-first responsive design
- [ ] Large touch targets for outdoor use
- [ ] No console errors

## Done Report
When complete, write your done report to: `coordination/frontend/outbox/005-done.md`
