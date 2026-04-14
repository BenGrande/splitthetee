# Task 002: Done Report — OSM Course Map + Hole Association Services & Endpoints

## Status: COMPLETE

## What Was Implemented

### 1. OSM Service (`api/app/services/golf/osm.py`)
- `query_overpass()` — queries Overpass API with retry logic (2 attempts per endpoint, 2s wait on 429/504, HTML response detection)
- `parse_overpass_features()` — converts raw Overpass elements to feature dicts with category mapping (fairway, green, tee, bunker, rough, hole, water, path, course_boundary, driving_range→fairway)
- `fetch_course_map()` — full flow with MongoDB caching via `map_cache` collection, radius capped at 3000m
- Overpass QL query matches the spec (ways + relations for golf, water, leisure)

### 2. Hole Association Service (`api/app/services/golf/holes.py`)
- `associate_features()` — core spatial matching algorithm ported from `hole-association.js`
  - Extracts and deduplicates holes by ref (keeps longest coordinate path)
  - Assigns non-hole features to nearest hole using min-distance with bbox pre-filter
  - Skips path features and course boundaries
  - Computes difficulty from handicap, or estimates from par/yardage ratio
- `_get_api_hole_data()` — extracts hole data from Golf API response (prefers longest male tee set)
- `_estimate_difficulty()` — difficulty rank estimation (1=hardest, 18=easiest)
- Helper functions: `_dist_sq`, `_min_dist_between`, `_bbox`, `_bbox_overlaps`

### 3. Course Map Endpoint (`api/app/api/v1/course_map.py`)
- `GET /api/v1/course-map?lat=<float>&lng=<float>&radius=<int>` — returns `{ features, center }`
- Delegates to OSM service, handles errors with 500 status

### 4. Course Holes Endpoint (`api/app/api/v1/holes.py`)
- `GET /api/v1/course-holes?lat=<float>&lng=<float>&courseId=<optional>` — returns `{ holes, course_name, center }`
- Bundle cache check → fetch map data → fetch course data (by courseId or search cache proximity) → associate features → cache result
- Proper error handling with logging

### 5. Unit Tests (74 total, all passing)
- `tests/test_osm.py` — 16 tests (category mapping, feature parsing, cache behavior)
- `tests/test_holes.py` — 17 tests (distance functions, bbox, API hole data extraction, difficulty estimation, full association)
- `tests/test_endpoints.py` — 6 tests (course-map and course-holes endpoints)
- Plus 24 existing tests from Task 001 (schemas + search) — all still passing

## Deviations from Spec
- None. Implementation faithfully ports the Node.js logic.

## How to Test
```bash
# Run all unit tests
cd api && .venv/bin/python -m pytest tests/ -v

# Manual test (requires MongoDB + Overpass API access)
# curl "http://localhost:8000/api/v1/course-map?lat=36.5626&lng=-121.9191&radius=2000"
# curl "http://localhost:8000/api/v1/course-holes?lat=36.5626&lng=-121.9191"
```
