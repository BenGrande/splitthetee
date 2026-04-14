# Task 001: Pydantic Schemas + Search Service & Endpoint

## Priority: HIGH — unblocks all other API work

## What to Build

### 1. Pydantic Schemas (`api/app/schemas/`)

Create response/request models used across the API. Reference the old Node stack for field shapes.

**`api/app/schemas/course.py`** — Course-related schemas:
```python
# CourseSearchResult — one item from search results
# Fields: id, name, club_name, location (city/state/country), lat, lng,
#         tees (list of TeeSet), holes (list of HoleInfo)
# TeeSet: tee_name, gender, par, rating, slope, yardage, holes (list of TeeHole)
# TeeHole: number, par, yardage, handicap
# HoleInfo: number, par, yardage, handicap
```

**`api/app/schemas/map.py`** — OSM/map feature schemas:
```python
# MapFeature — one OSM feature
# Fields: id (str), category (str — fairway/green/tee/bunker/rough/hole/water/path/course_boundary),
#         ref (optional str), par (optional int), name (optional str),
#         coords (list of [float, float])

# CourseMapResponse: features (list[MapFeature]), center ([float, float])
```

**`api/app/schemas/hole.py`** — Hole bundle schemas:
```python
# HoleBundle — one hole with associated features
# Fields: ref (int), par (int), yardage (int), handicap (int), difficulty (float),
#         route_coords (list of [float, float]), features (list[MapFeature])

# CourseHolesResponse: holes (list[HoleBundle]), center ([float, float]), course_name (str)
```

**`api/app/schemas/settings.py`** — Settings schemas:
```python
# DesignSettings — saved glass design config (flexible dict)
# SaveSettingsRequest: course_name (str), settings (dict)
# SettingsListItem: filename (str), course_name (str), saved_at (str)
```

### 2. Search Service (`api/app/services/golf/search.py`)

Port from `server.js` lines ~47-95 (`/api/search` handler). Logic:

1. Accept query string `q`
2. Check MongoDB `search_cache` collection for cached result (key: sanitized query)
3. If cached and not expired (7-day TTL managed by MongoDB TTL index), return cached data
4. Otherwise, call Golf Course API: `GET {GOLF_API_BASE}/search?search_query={q}`
   - Header: `Authorization: Key {GOLF_API_KEY}`
   - Use `httpx.AsyncClient` for the request
5. Parse response — extract courses array from API response
6. Store in MongoDB `search_cache`: `{ query: sanitized_q, data: courses, created_at: utcnow }`
7. Return courses array

**Important**: The Golf API key is in `api/app/core/config.py` as `GOLF_API_KEY`. It's loaded from `.env`. Check if `.env` exists; if not, read the key from `/Users/contextuallabs/code/one-nine/api_key.md`.

### 3. Search Endpoint (`api/app/api/v1/search.py`)

Update the existing stub:
- `GET /api/v1/search?q=<query>`
- Call the search service
- Return `{ "courses": [...] }` matching the old API shape
- Handle empty query (return empty array)
- Handle API errors gracefully (return error message with 502 status)

## Reference Files (READ ONLY — do not modify)
- `/Users/contextuallabs/code/one-nine/server.js` — lines 47-95 for search logic
- `/Users/contextuallabs/code/one-nine/api_key.md` — Golf API key

## Files to Create/Modify
- CREATE: `api/app/schemas/course.py`
- CREATE: `api/app/schemas/map.py`
- CREATE: `api/app/schemas/hole.py`
- CREATE: `api/app/schemas/settings.py`
- MODIFY: `api/app/services/golf/search.py`
- MODIFY: `api/app/api/v1/search.py`

## Definition of Done
- [ ] All schema files created with proper Pydantic v2 models
- [ ] Search service fetches from Golf Course API with MongoDB caching
- [ ] `GET /api/v1/search?q=pebble` returns real course data
- [ ] Empty query returns `{ "courses": [] }`
- [ ] API errors return proper HTTP error responses
- [ ] No modifications to old Node stack files

## Done Report
When complete, write your done report to: `coordination/api/outbox/001-done.md`
Include: what was implemented, any deviations from spec, how to test.
