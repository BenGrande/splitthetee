# Task 024: Unify Glass Preview and Cricut Export Rendering (Phase A)

**Priority**: Critical — ALL other tasks depend on this
**Depends on**: Nothing

**CRITICAL**: This is the most important architectural change. The cricut white layer must use the SAME rendering code as the glass preview. Currently `render_cricut_white()` in `cricut.py` is a completely separate pipeline from `_render_vinyl_preview()` in `svg.py` — they've diverged, causing export/preview mismatch.

---

## The Fix

Refactor `_render_vinyl_preview()` in `svg.py` to accept a `layer` parameter:

```python
def _render_vinyl_preview(layout, opts, terrain_zones=None, layer="all"):
    """
    layer="all"   → full glass preview (current behavior: background + all colors)
    layer="white"  → only white elements, no background (for cricut white export)
    layer="green"  → only green elements (for cricut green export)
    layer="blue"   → only blue elements (for cricut blue export)
    layer="tan"    → only tan elements (for cricut tan export)
    """
```

### What changes per layer:

**layer="all" (glass preview):**
- Dark background (`#1a1a1a`)
- All white elements (outlines, ruler, text, zone boundaries, etc.)
- All green elements (green/tee strokes, fairway fills)
- All blue elements (water fills)
- All tan elements (bunker fills)
- Glass outline

**layer="white" (cricut white):**
- NO background
- White feature outlines (fairway, rough, path, boundary)
- White scoring zone boundary lines + score numbers
- White hole number circles + dashed lines to tees
- White stats boxes (rounded rect + stacked text) — SAME design as preview
- White ruler (full design) — SAME as preview
- White course name + hole range
- White logo
- White glass outline
- NO green/blue/tan elements

**layer="green" (cricut green):**
- Fairway fills (solid green)
- Green outlines (greens, tees)
- Score number knockouts where overlapping

**layer="blue" (cricut blue):**
- Water fills (solid blue)
- Score number knockouts where overlapping

**layer="tan" (cricut tan):**
- Bunker fills (tan)

### Update `cricut.py`

Rewrite the cricut render functions to call through to the shared renderer:

```python
def render_cricut_white(layout, zones_by_hole, template, opts):
    return _render_vinyl_preview(layout, opts, terrain_zones=..., layer="white")

def render_cricut_green(layout, zones_by_hole, template, opts):
    return _render_vinyl_preview(layout, opts, terrain_zones=..., layer="green")

def render_cricut_blue(layout, zones_by_hole, template, opts):
    return _render_vinyl_preview(layout, opts, terrain_zones=..., layer="blue")

def render_cricut_tan(layout, zones_by_hole, template, opts):
    return _render_vinyl_preview(layout, opts, terrain_zones=..., layer="tan")
```

The guide layer can remain separate (it's a reference overlay, not a print layer).

### Implementation Approach

1. Add the `layer` parameter to `_render_vinyl_preview()`
2. Wrap each rendering section in a layer check:
   - Background: only when `layer == "all"`
   - White elements: when `layer in ("all", "white")`
   - Green elements: when `layer in ("all", "green")`
   - Blue elements: when `layer in ("all", "blue")`
   - Tan elements: when `layer in ("all", "tan")`
3. Update `cricut.py` to call through to the shared function
4. Remove the old independent rendering code from `cricut.py` (keep only the guide layer)
5. Ensure `render.py` passes all required data (terrain_zones, course_name, hole_range, etc.) to both paths

### What to Preserve from cricut.py
- `render_cricut_guide()` — keep as-is (separate reference overlay)
- Any compact arrangement logic for green/tan/blue pieces — this is cricut-specific (arranging cut pieces efficiently on a vinyl sheet). If this exists, keep it as a separate post-processing step

## Files to Modify
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Add `layer` parameter to `_render_vinyl_preview()`; wrap sections in layer checks |
| `api/app/services/render/cricut.py` | Rewrite `render_cricut_white/green/blue/tan` to call shared renderer; keep guide layer |
| `api/app/api/v1/render.py` | Ensure all data flows through to both preview and export paths |

## Definition of Done
1. Glass preview and cricut white layer produce identical white elements
2. Cricut green/blue/tan layers match their respective glass preview elements
3. All rendering improvements (stats boxes, ruler, zone boundaries) automatically appear in exports
4. Guide layer still works independently
5. All existing tests pass (update as needed for new function signatures)
6. Visually verify: export white SVG opened in browser looks identical to glass preview white elements
