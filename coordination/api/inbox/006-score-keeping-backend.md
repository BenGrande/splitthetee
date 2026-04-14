# Task 006: Score-Keeping Backend (Phase 4)

## Priority: MEDIUM — separate feature track from designer

## Prerequisites
- Phase 1 complete (MongoDB, schemas working)

## What to Build

### 1. Glass Set & QR Code System (`api/app/api/v1/qr.py` + `api/app/services/`)

**Glass Set Creation:**
- `POST /api/v1/glass-sets` — create a new glass set
  - Body: `{ course_id, course_name, glass_count, holes_per_glass }`
  - Generate unique glass set ID (short, URL-safe — e.g., 8-char alphanumeric)
  - Generate QR code for each glass in the set
  - QR URL format: `{FRONTEND_URL}/play/{glass_set_id}?glass={glass_number}`
  - Store in MongoDB `glass_sets` collection
  - Return: `{ id, qr_codes: [{ glass_number, url, qr_svg }] }`

**QR Code Generation:**
- Use the `qrcode` library (already in pyproject.toml)
- Generate SVG format QR codes (for embedding in glass SVG)
- Each QR encodes: glass set ID + glass number
- Small size suitable for glass bottom area

**Glass Set Retrieval:**
- `GET /api/v1/glass-sets/{glass_set_id}` — get glass set details
  - Return: full glass set doc with QR codes, course info

### 2. Game Session System (`api/app/api/v1/games.py`)

**Join Game:**
- `POST /api/v1/games/join`
  - Body: `{ glass_set_id, player_name }`
  - Find or create game session for this glass set
  - Register player in session
  - Return: `{ session_id, player_id, player_name, session: { players, course_name, glass_count, holes_per_glass } }`
  - If session exists and is active, just add player
  - If no session, create one linked to the glass set

**Get Session:**
- `GET /api/v1/games/{session_id}`
  - Return: full session with players list and course config

**Submit Score:**
- `POST /api/v1/games/{session_id}/score`
  - Body: `{ player_id, hole_number, glass_number, score }`
  - Score range: -1 to 8 (validate!)
  - Upsert: if player already has score for this hole, update it
  - Return: `{ ok: true, score_record }`

**Get Leaderboard:**
- `GET /api/v1/games/{session_id}/leaderboard`
  - Aggregate scores per player across all holes
  - Return sorted by cumulative score (lowest first — golf scoring):
  ```json
  {
    "leaderboard": [
      {
        "player_id": "...",
        "player_name": "...",
        "total_score": 12,
        "holes_played": 14,
        "scores_by_hole": [
          { "hole_number": 1, "glass_number": 1, "score": 2 },
          ...
        ]
      }
    ],
    "course_name": "...",
    "total_holes": 18
  }
  ```

**Get Player Scores:**
- `GET /api/v1/games/{session_id}/scores/{player_id}`
  - Return all scores for a specific player
  - Organized by glass → hole

### 3. Pydantic Schemas

**`api/app/schemas/game.py`** (new):
```python
class GlassSetCreate(BaseModel):
    course_id: str
    course_name: str
    glass_count: int = 3
    holes_per_glass: int = 6

class QRCode(BaseModel):
    glass_number: int
    url: str
    qr_svg: str

class GlassSetResponse(BaseModel):
    id: str
    course_id: str
    course_name: str
    glass_count: int
    holes_per_glass: int
    created_at: str
    qr_codes: list[QRCode]

class JoinGameRequest(BaseModel):
    glass_set_id: str
    player_name: str

class JoinGameResponse(BaseModel):
    session_id: str
    player_id: str
    player_name: str

class ScoreSubmit(BaseModel):
    player_id: str
    hole_number: int
    glass_number: int
    score: int  # -1 to 8

class LeaderboardEntry(BaseModel):
    player_id: str
    player_name: str
    total_score: int
    holes_played: int
    scores_by_hole: list[dict]

class LeaderboardResponse(BaseModel):
    leaderboard: list[LeaderboardEntry]
    course_name: str
    total_holes: int
```

### 4. Game Service (`api/app/services/game.py`)

Encapsulate game logic:
- `create_glass_set(data)` — generate IDs, QR codes, store in MongoDB
- `find_or_create_session(glass_set_id)` — find active session or create new
- `add_player(session_id, name)` — register player
- `submit_score(session_id, player_id, hole, glass, score)` — upsert score
- `get_leaderboard(session_id)` — aggregate and sort scores
- `generate_qr_svg(url)` — create QR code as SVG string

## Files to Create/Modify
- CREATE: `api/app/schemas/game.py`
- CREATE: `api/app/services/game.py`
- MODIFY: `api/app/api/v1/games.py` (replace stubs with real logic)
- MODIFY: `api/app/api/v1/qr.py` (replace stubs with real logic)

## Definition of Done
- [ ] `POST /api/v1/glass-sets` creates glass set with QR codes (SVG format)
- [ ] `GET /api/v1/glass-sets/{id}` returns glass set with QR data
- [ ] `POST /api/v1/games/join` creates/joins session and registers player
- [ ] `POST /api/v1/games/{id}/score` submits and upserts scores
- [ ] `GET /api/v1/games/{id}/leaderboard` returns sorted cumulative leaderboard
- [ ] Score validation (-1 to 8 range)
- [ ] Multiple players in same session works
- [ ] All Pydantic schemas defined and used
- [ ] Tests cover all endpoints and edge cases

## Done Report
When complete, write your done report to: `coordination/api/outbox/006-done.md`
