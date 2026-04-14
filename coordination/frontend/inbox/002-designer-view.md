# Task 002: Port Glass Designer View from designer.html to Vue

## Priority: HIGH — core feature of the app

## Prerequisites
- Task 001 (SearchView) should be complete so navigation works

## What to Build

Port the glass designer tool from `public/designer.html` (~782 lines) into the Vue `DesignerView.vue`. This is the main design tool for configuring glass layouts.

### Layout Structure

**Three-column layout:**
1. **Left sidebar** (~300px): All controls
2. **Center**: SVG preview area (main content)
3. **Right sidebar** (~200px): Layer visibility toggles + style editor

### Left Sidebar Controls

#### Course Section
- Course name display (from store/route params)
- Search box to switch courses (reuse CourseCard if created in Task 001)

#### Glass Configuration
- **Glass count**: Radio/button group — 1, 2, 3, 6
- **Holes per glass**: Auto-calculated from total holes / glass count
- **Glass dimensions** (number inputs with labels):
  - Height (mm, default 146)
  - Top radius (mm, default 43)
  - Bottom radius (mm, default 30)
  - Wall thickness (mm, default 3)
  - Base thickness (mm, default 5)
- **Fill mode**: Dropdown — "Full glass", "355ml can", "Custom"
  - Custom shows padding input

#### View Controls
- **Current glass**: Selector to view glass 1, 2, 3, etc.
- **Preview mode**: Toggle between "Glass" (warped) and "Rect" (flat)
- **Zoom**: Zoom in/out buttons + reset

#### Text & Logo
- **Font selector**: Dropdown with Google Font options
- **Logo upload**: File input for logo image (replaces course name text)
- **Show text**: Toggle

### Center Preview Area
- Renders SVG from the API (`POST /api/v1/render`)
- Pan (mouse drag) and zoom (mouse wheel) interaction
- Re-renders when any control changes (debounced ~300ms)
- Shows loading spinner during render

### Right Sidebar

#### Layer Toggles
Checkboxes for each layer (all on by default):
- Background
- Rough
- Fairway
- Water
- Bunker
- Tee
- Green
- Hole numbers
- Par labels

#### Style Editor
Per-layer color controls (only for visible layers):
- Fill color (color picker input)
- Stroke color (color picker input)
- Stroke width (number input)

Use the default style values from `svg-renderer.js`:
```
background: #1a472a
rough: fill #8ab878
fairway: fill #4a8f3f, stroke #3d7a34
bunker: fill #e8dca0, stroke #d4c87a
water: fill #5b9bd5, stroke #4a87be
tee: fill #7bc96a, stroke #5eaa50
green: fill #5cc654, stroke #3eaa36
```

### Bottom Action Bar
- **Export SVG**: Download current glass SVG
- **Export All**: Download all glasses as ZIP (if multiple glasses)
- **Save Settings**: Save current config to API
- **Load Settings**: Open modal listing saved configs from API

### State Management

Create a new Pinia store: `frontend/src/stores/designer.ts`

State to track:
```typescript
{
  glassCount: number       // 1, 2, 3, or 6
  currentGlass: number     // which glass is being viewed
  glassDimensions: { height, topRadius, bottomRadius, wallThickness, baseThickness }
  fillMode: 'full' | 'can' | 'custom'
  customPadding: number
  previewMode: 'glass' | 'rect'
  hiddenLayers: Set<string>
  styles: Record<string, { fill, stroke, strokeWidth }>
  fontFamily: string
  logoDataUrl: string | null
  showText: boolean
  svgContent: string       // current rendered SVG
  loading: boolean
}
```

Actions:
- `renderPreview()` — calls `POST /api/v1/render` with current state + course holes from course store
- `exportSvg()` — download current SVG as file
- `saveSettings(courseName)` — POST to `/api/v1/settings`
- `loadSettings(id)` — GET from `/api/v1/settings/{id}` and apply

### API Integration

The designer calls these API endpoints:
- `POST /api/v1/render` — get SVG preview (may not exist yet — handle gracefully, show placeholder)
- `POST /api/v1/render/glass-template` — get glass geometry (may not exist yet)
- `POST /api/v1/settings` — save
- `GET /api/v1/settings` — list
- `GET /api/v1/settings/{id}` — load

**Important**: The render endpoints may not be implemented yet (API Task 003). Build the UI to work with them when available, but show a placeholder SVG or "API not available" message if they return errors.

### Styling
- Tailwind CSS
- Dark theme (`bg-gray-900`) for sidebars
- Controls: compact, professional look
- Color pickers: use native `<input type="color">`
- Preview area: neutral background with subtle grid/pattern

## Reference Files (READ ONLY)
- `/Users/contextuallabs/code/one-nine/public/designer.html` — old designer to port from
- `/Users/contextuallabs/code/one-nine/public/svg-renderer.js` — default styles
- `/Users/contextuallabs/code/one-nine/public/glass-template.js` — glass dimension defaults

## Files to Create/Modify
- MODIFY: `frontend/src/views/DesignerView.vue` (replace stub)
- CREATE: `frontend/src/stores/designer.ts`
- CREATE: `frontend/src/components/LayerControls.vue` (layer toggles + style editor)
- CREATE: `frontend/src/components/GlassControls.vue` (glass config controls)
- CREATE: `frontend/src/components/SvgPreview.vue` (SVG display with pan/zoom)

## Definition of Done
- [ ] Three-column layout renders correctly
- [ ] All glass dimension controls work and update state
- [ ] Glass count selector (1/2/3/6) works
- [ ] Layer toggles show/hide layers in state
- [ ] Style editor updates colors in state
- [ ] Preview mode toggle (glass/rect) updates state
- [ ] Export SVG button downloads SVG file (even if placeholder)
- [ ] Save/load settings talks to API (graceful failure if API not ready)
- [ ] SVG preview area has pan/zoom interaction
- [ ] Designer store created and wired up
- [ ] No console errors
- [ ] Responsive — functional on desktop, reasonable on tablet

## Done Report
When complete, write your done report to: `coordination/frontend/outbox/002-done.md`
