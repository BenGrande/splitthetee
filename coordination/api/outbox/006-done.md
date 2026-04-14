# Task 006: Done Report — Score-Keeping Backend (Phase 4)

## Status: COMPLETE

## What Was Implemented

### 1. Game Schemas (`api/app/schemas/game.py`)
- `GlassSetCreate` — course_id, course_name, glass_count (default 3), holes_per_glass (default 6)
- `QRCode` — glass_number, url, qr_svg
- `GlassSetResponse` — full glass set with QR codes
- `JoinGameRequest` — glass_set_id, player_name
- `JoinGameResponse` — session_id, player_id, player_name
- `ScoreSubmit` — player_id, hole_number, glass_number, score (validated -1 to 8)
- `LeaderboardEntry` — player stats with scores_by_hole
- `LeaderboardResponse` — sorted leaderboard with course info

### 2. Game Service (`api/app/services/game.py`)
- `_generate_id(length)` — URL-safe alphanumeric IDs (secrets-based)
- `generate_qr_svg(url)` — QR code as SVG string using `qrcode` library
- `create_glass_set(data)` — generates glass set ID, creates QR codes for each glass, stores in MongoDB
- `get_glass_set(id)` — retrieves glass set by ID
- `find_or_create_session(glass_set_id)` — finds active session or creates new one linked to glass set
- `add_player(session_id, name)` — registers player in session
- `get_session(session_id)` — returns session with player list
- `submit_score(session_id, player_id, hole, glass, score)` — upserts score in MongoDB
- `get_leaderboard(session_id)` — aggregates per-player scores, sorts by total (lowest first)
- `get_player_scores(session_id, player_id)` — returns player's scores sorted by hole

### 3. Glass Set / QR Endpoints (`api/app/api/v1/qr.py`)
- `POST /api/v1/glass-sets` — creates glass set with QR codes (SVG format)
  - QR URLs: `{FRONTEND_URL}/play/{glass_set_id}?glass={glass_number}`
- `GET /api/v1/glass-sets/{id}` — retrieves glass set with QR data

### 4. Game Endpoints (`api/app/api/v1/games.py`)
- `POST /api/v1/games/join` — joins/creates session, registers player
- `GET /api/v1/games/{session_id}` — full session with players
- `POST /api/v1/games/{session_id}/score` — submits score (validated -1 to 8)
- `GET /api/v1/games/{session_id}/leaderboard` — cumulative leaderboard (golf scoring, lowest first)
- `GET /api/v1/games/{session_id}/scores/{player_id}` — player's scores by hole

### 5. Unit Tests (217 total, all passing)
- `test_game.py` — 33 tests covering:
  - ID generation (length, uniqueness, alphanumeric)
  - QR SVG generation
  - All Pydantic schemas (validation including score range -1 to 8)
  - Service functions (create glass set, find/create session, submit score, leaderboard aggregation)
  - All endpoints (glass set CRUD, join game, score submission, validation, leaderboard, player scores)
- All 184 existing tests still passing

## Deviations from Spec
- None. All specified features implemented.

## How to Test
```bash
cd api && .venv/bin/python -m pytest tests/ -v

# Create glass set
# POST /api/v1/glass-sets { "course_id": "123", "course_name": "Pebble Beach" }

# Join game
# POST /api/v1/games/join { "glass_set_id": "abc123", "player_name": "Alice" }

# Submit score
# POST /api/v1/games/{session_id}/score { "player_id": "p1", "hole_number": 1, "glass_number": 1, "score": 3 }

# Get leaderboard
# GET /api/v1/games/{session_id}/leaderboard
```
