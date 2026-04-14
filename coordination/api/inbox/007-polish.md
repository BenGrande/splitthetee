# Task 007: Phase 5 — API Polish & Integration

## Priority: MEDIUM — final polish pass

## What to Build

### 1. Logo Integration in SVG

The One Nine logo (`public/logo.png` at project root) should be embeddable in glass SVGs.

**Add logo endpoint:**
- `GET /api/v1/assets/logo` — returns the logo as a base64 data URL
- Read from `public/logo.png` (or a configured path)
- Cache the data URL in memory after first read

**Logo in SVG rendering:**
- When `logo_url` is provided in render options, the SVG renderer already supports it
- Ensure it renders correctly at the bottom-left of the glass layout
- In Cricut white layer: logo should render as an outline/silhouette suitable for vinyl cutting
- Verify logo positioning in both rect and glass modes

### 2. QR Code Embedding in Glass SVG

When rendering a glass that has a glass_set_id:
- Accept `qr_svg` or `glass_set_id` in render options
- If `glass_set_id` provided, fetch QR code from the glass set record
- Embed QR code SVG at bottom-right of glass layout (next to logo)
- QR should be small (~15mm square on the physical glass)
- In Cricut white layer: QR code included as cut paths

**Add to render options:**
```python
qr_svg: Optional[str] = None      # pre-generated QR SVG to embed
glass_set_id: Optional[str] = None # fetch QR from glass set record
glass_number: Optional[int] = None # which glass in the set (for QR lookup)
```

### 3. Scoring Zone Fine-Tuning

Make scoring zone computation smarter:

**Per-hole zone adjustment based on:**
- **Green size**: Larger greens get more generous -1 zone
- **Par**: Par 3s have tighter zones (precision holes), par 5s more forgiving
- **Difficulty/handicap**: Harder holes get slightly wider zones overall
- Add `difficulty_factor` to zone computation that scales zone widths

**Configurable overshoot penalty:**
- Add `overshoot_penalty` to render options (default 5, can be 8)
- Display in ruler if space allows

### 4. Course Font Intelligence

The plan mentions intelligently sourcing fonts from the course's website:
- Add a `font_hint` field to course search results
- For now, implement a simple mapping of well-known courses to fonts
- Create `api/app/services/font_hints.py` with a dict:
  ```python
  COURSE_FONTS = {
      "pebble beach": "Playfair Display",
      "augusta national": "Cormorant Garamond",
      "st andrews": "EB Garamond",
      # etc.
  }
  def get_font_hint(course_name: str) -> str | None
  ```
- Include `font_hint` in course-holes response so frontend can use it as default

### 5. API Health & Error Improvements

- Add `/api/v1/status` endpoint returning:
  - API version
  - MongoDB connection status
  - Cache stats (search/map/bundle counts)
  - Active game sessions count
- Improve error messages across all endpoints (consistent format)
- Add request logging middleware (log endpoint, duration, status code)

### 6. Data Cleanup

- Ensure all MongoDB TTL indexes are properly configured
- Add a `POST /api/v1/admin/cleanup` endpoint to manually clear expired caches
- Add index on `game_sessions.status` for active session queries

## Files to Create/Modify
- CREATE: `api/app/services/font_hints.py`
- CREATE: `api/app/api/v1/assets.py` (logo endpoint)
- MODIFY: `api/app/services/render/svg.py` (QR embedding, logo positioning)
- MODIFY: `api/app/services/render/cricut.py` (QR in white layer)
- MODIFY: `api/app/services/render/scoring.py` (difficulty-based zone adjustment)
- MODIFY: `api/app/api/v1/render.py` (QR/logo options)
- MODIFY: `api/app/api/v1/holes.py` (include font_hint in response)
- MODIFY: `api/app/api/router.py` (register assets router)
- MODIFY: `api/app/main.py` (logging middleware, status endpoint)

## Definition of Done
- [ ] Logo renders at bottom-left of glass SVGs (both modes)
- [ ] QR code embeds at bottom-right when glass_set_id provided
- [ ] Scoring zones adjust based on green size, par, difficulty
- [ ] Font hints returned for known courses
- [ ] `/api/v1/status` endpoint works
- [ ] Request logging middleware active
- [ ] Tests cover new features

## Done Report
When complete, write your done report to: `coordination/api/outbox/007-done.md`
