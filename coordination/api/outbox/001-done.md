# Task 001: Done Report — Pydantic Schemas + Search Service & Endpoint

## Status: COMPLETE

## What Was Implemented

### 1. Pydantic Schemas (all created)
- **`api/app/schemas/course.py`** — `CourseSearchResult`, `TeeSet`, `TeeHole`, `HoleInfo`
- **`api/app/schemas/map.py`** — `MapFeature`, `CourseMapResponse`
- **`api/app/schemas/hole.py`** — `HoleBundle`, `CourseHolesResponse`
- **`api/app/schemas/settings.py`** — `DesignSettings`, `SaveSettingsRequest`, `SettingsListItem`

### 2. Search Service (`api/app/services/golf/search.py`)
- Accepts query string, sanitizes for cache key
- Checks MongoDB `search_cache` collection for cached results
- On cache miss, calls Golf Course API (`GET /v1/search?search_query=...`) with auth header
- Stores results in MongoDB with `cached_at` timestamp (TTL managed by existing MongoDB index)
- Uses `httpx.AsyncClient` for async HTTP calls

### 3. Search Endpoint (`api/app/api/v1/search.py`)
- `GET /api/v1/search?q=<query>` — returns `{ "courses": [...] }`
- Empty/missing query returns `{ "courses": [] }`
- Golf API HTTP errors return 502 with descriptive message
- Network/connection errors return 502

### 4. Unit Tests (24 tests, all passing)
- **`tests/test_schemas.py`** — 12 tests covering all schema models
- **`tests/test_search.py`** — 12 tests covering sanitization, service logic (cache hit/miss/error), and endpoint behavior

## Deviations from Spec
- None. Implementation follows the spec exactly.

## How to Test
```bash
# Run unit tests
cd api && .venv/bin/python -m pytest tests/ -v

# Manual test (requires MongoDB running and .env with GOLF_API_KEY)
# curl "http://localhost:8000/api/v1/search?q=pebble"
# curl "http://localhost:8000/api/v1/search"  # returns {"courses": []}
```
