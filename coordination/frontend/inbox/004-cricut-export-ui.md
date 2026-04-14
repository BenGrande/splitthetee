# Task 004: Cricut Export UI in Designer (Phase 3)

## Priority: HIGH — production workflow feature

## Prerequisites
- Designer view working (Frontend Tasks 001-003)
- Cricut API endpoints may not be ready yet — design UI to degrade gracefully

## What to Build

### 1. Cricut Export Panel

Add a "Cricut Export" section to the designer, either in the left sidebar or as a modal/panel.

**Controls:**
- **"Export for Cricut" button** — primary action, opens Cricut export panel/modal
- **Layer previews**: Three preview thumbnails showing:
  - White layer (outlines, text, ruler)
  - Green layer (greens, tees — compact arrangement)
  - Tan layer (bunkers — compact arrangement)
- **Individual layer download**: Button per layer to download just that SVG
- **Download All**: Single button that downloads a ZIP with all three layers + placement guide
- **Scale info**: Display "Print at 100% scale — verify with 10mm reference bar"

### 2. Cricut Preview Mode

Add a "Cricut" preview mode option (4th mode alongside Glass/Rect/Scoring):
- When "Cricut White" selected: preview shows the white layer SVG
- When "Cricut Green" selected: preview shows the compact green pieces
- When "Cricut Tan" selected: preview shows the compact tan pieces

Update `previewMode` type to include: `'cricut-white' | 'cricut-green' | 'cricut-tan'`

### 3. API Integration

Call `POST /api/v1/render/cricut` endpoint:
```
Body: { holes, options: { ...same as render... } }
Response: { white: "<svg>", green: "<svg>", tan: "<svg>", guide: "<svg>" }
```

If endpoint not available yet, show "Cricut export coming soon" placeholder.

For individual layer preview, call `POST /api/v1/render` with `mode: "cricut-white"` etc.

### 4. Implementation

**In designer store (`stores/designer.ts`):**
- Add `cricutSvgs: { white: string, green: string, tan: string, guide: string } | null`
- Add `exportCricut()` action — calls `/api/v1/render/cricut`, stores results, triggers ZIP download
- Add `previewCricutLayer(layer)` action — calls render with cricut mode for preview

**In DesignerView.vue or new CricutExportPanel.vue:**
- Cricut export button in bottom action bar (next to existing Export SVG)
- Modal or expandable panel with the three layer previews + download buttons

### 5. Placement Guide Display

The API returns a `guide` SVG showing the full glass layout with numbered markers for where each green/tan piece goes. Display this:
- As a fourth preview option in the Cricut panel
- Or as a printable reference that can be downloaded separately

## Files to Modify
- MODIFY: `frontend/src/stores/designer.ts` (cricut modes, exportCricut action)
- MODIFY: `frontend/src/views/DesignerView.vue` (Cricut export button, modal/panel)
- MODIFY: `frontend/src/components/GlassControls.vue` (cricut preview modes)
- POSSIBLY CREATE: `frontend/src/components/CricutExportPanel.vue`

## Definition of Done
- [ ] "Export for Cricut" button in designer bottom bar
- [ ] Cricut export panel/modal shows three layer previews
- [ ] Individual layer download works (SVG files)
- [ ] "Download All" creates ZIP with white/green/tan SVGs + guide
- [ ] Cricut preview modes show individual layers in main preview
- [ ] Graceful fallback if API endpoint not ready
- [ ] Scale verification info displayed

## Done Report
When complete, write your done report to: `coordination/frontend/outbox/004-done.md`
