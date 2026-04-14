# Task 002: OSM Course Map + Hole Association Services & Endpoints

## Priority: HIGH — needed for designer to show course data

## Prerequisites
- Task 001 (schemas) must be complete — you need MapFeature, HoleBundle schemas

## What to Build

### 1. OSM Service (`api/app/services/golf/osm.py`)

Port from `server.js` lines ~97-185 (`/api/course-map` handler). Logic:

1. Accept `lat`, `lng`, `radius` (default 2000m, max 3000m)
2. Check MongoDB `map_cache` for cached result (key: `{lat}_{lng}_{radius}`)
3. If cached, return it
4. Build Overpass QL query (COPY this exactly from server.js ~line 109-130):
   ```
   [out:json][timeout:30];
   (
     way["golf"](around:{radius},{lat},{lng});
     relation["golf"](around:{radius},{lat},{lng});
     way["natural"="water"](around:{radius},{lat},{lng});
     relation["natural"="water"](around:{radius},{lat},{lng});
     way["water"](around:{radius},{lat},{lng});
     relation["water"](around:{radius},{lat},{lng});
     way["leisure"="golf_course"](around:{radius},{lat},{lng});
     relation["leisure"="golf_course"](around:{radius},{lat},{lng});
   );
   out body;
   >;
   out skel qt;
   ```
5. POST to Overpass API endpoints (try each from `settings.OVERPASS_ENDPOINTS`)
   - Retry logic: 2 attempts per endpoint
   - On 429/504: wait 2 seconds then retry
   - Use `httpx.AsyncClient` with 30s timeout
6. Parse OSM response — convert elements to MapFeature list:
   - Build node lookup from `node` elements
   - For `way` elements: resolve node refs to coords, determine category from tags
   - Category mapping (from server.js ~line 142-160):
     - `golf=fairway` → fairway
     - `golf=green/putting_green` → green
     - `golf=tee` → tee
     - `golf=bunker` → bunker
     - `golf=rough` → rough
     - `golf=hole` → hole
     - `golf=water_hazard` or `natural=water` or has `water` tag → water
     - `golf=path/cartpath` → path
     - `leisure=golf_course` → course_boundary
   - Extract `ref` (hole number), `par`, `name` from tags
7. Compute center as average of all coordinates
8. Cache in MongoDB `map_cache`: `{ cache_key, features, center, created_at }`
9. Return `{ features, center }`

### 2. Hole Association Service (`api/app/services/golf/holes.py`)

Port from `hole-association.js` (~205 lines). This is the core spatial matching algorithm.

**Main function: `associate_features(features, course_data)`**

Algorithm:
1. Extract hole features (category == "hole" with a ref number)
2. Deduplicate holes by ref — keep the one with the longest coordinate path
3. If course_data provided, extract hole stats (par, yardage, handicap) from tee sets
   - Prefer male tees, select the longest tee set
4. For each non-hole feature:
   - Calculate minimum distance to each hole's route coordinates
   - Assign feature to the nearest hole
5. Compute difficulty score per hole:
   - Use handicap if available (from API data)
   - Otherwise estimate from yardage/par ratio
   - Formula: `18 - (yardage/expected - 0.7) * (17/0.6)`
   - Expected yardage: par 3 = 170, par 4 = 400, par 5 = 530
6. Return list of HoleBundle objects

**Helper functions needed:**
- `point_to_polyline_distance(point, polyline)` — min distance from point to any segment of polyline
- `feature_to_hole_distance(feature, hole)` — min distance across all point pairs
- `bbox_overlap(bbox1, bbox2)` — check if bounding boxes overlap (optimization)

### 3. Course Holes Endpoint (`api/app/api/v1/holes.py`)

Port from `server.js` lines ~187-240 (`/api/course-holes` handler):

1. `GET /api/v1/course-holes?lat=<float>&lng=<float>&courseId=<optional>`
2. Check MongoDB `bundle_cache` for cached result
3. Fetch map data via OSM service
4. If `courseId` provided, fetch course details from Golf Course API: `GET {GOLF_API_BASE}/courses/{courseId}`
   - Same auth header as search
5. If no courseId, try to find matching course in `search_cache` by lat/lng proximity
6. Call `associate_features(features, course_data)`
7. Cache result in `bundle_cache`
8. Return `{ holes: [...], center: [...], course_name: "..." }`

### 4. Course Map Endpoint (`api/app/api/v1/course_map.py`)

Update the existing stub:
- `GET /api/v1/course-map?lat=<float>&lng=<float>&radius=<int>`
- Call OSM service
- Return `{ features: [...], center: [...] }`

## Reference Files (READ ONLY — do not modify)
- `/Users/contextuallabs/code/one-nine/server.js` — lines 97-240
- `/Users/contextuallabs/code/one-nine/hole-association.js` — full file

## Files to Create/Modify
- MODIFY: `api/app/services/golf/osm.py`
- MODIFY: `api/app/services/golf/holes.py`
- MODIFY: `api/app/api/v1/holes.py`
- MODIFY: `api/app/api/v1/course_map.py`

## Definition of Done
- [ ] OSM service fetches and parses Overpass data correctly
- [ ] Retry logic with dual endpoints works
- [ ] Hole association correctly groups features to holes
- [ ] `GET /api/v1/course-map?lat=36.5626&lng=-121.9191&radius=2000` returns features
- [ ] `GET /api/v1/course-holes?lat=36.5626&lng=-121.9191` returns bundled holes
- [ ] MongoDB caching works for both endpoints
- [ ] All responses use Pydantic schemas from Task 001

## Done Report
When complete, write your done report to: `coordination/api/outbox/002-done.md`
