# Task 020: Print Accuracy (Remove Glow/Fills) + Thinner Outlines — DONE

## Summary
Removed all non-print visual effects (beer gradient, amber glow, terrain zone fills) and reduced stroke widths for accurate vinyl print preview.

## Part 1: Remove Fake Effects

### A. Amber glow removed
- Removed the entire `layer-green_interior` section that rendered `rgba(255,180,50,0.15)` fills under green features
- Green outlines are now green stroke on dark background only

### B. Beer gradient removed
- Removed `beerGrad` linearGradient definition from `<defs>`
- Background now uses solid dark color `#1a1a1a` (represents clear glass)
- No beer color simulation

### C. Terrain zone fills verified clean
- Vinyl mode already used `fill="none"` for terrain zone polygons — confirmed correct
- Only white stroke boundary lines render (these correspond to actual vinyl scoring zone markers)

### D. Print accuracy verified
Every visible element corresponds to a vinyl cut:
- White: feature outlines, hole numbers, stats, ruler, zone boundaries, text
- Green: green/tee outlines, filled fairway
- Blue: filled water
- Tan: filled bunkers
- Nothing else

## Part 2: Thinner Outlines

### svg.py stroke widths
| Element | Old | New |
|---------|-----|-----|
| White features (rough/path/boundary) | 0.8 | **0.4** |
| Green outlines (green/tee) | 1.0 | **0.6** |
| Fairway fill stroke | 0.3 | **0.2** |
| Water fill stroke | 0.3 | **0.2** |
| Terrain zone boundaries | 0.5 | **0.3** |

### cricut.py stroke widths
- White layer main stroke: 0.5 → **0.4**

## Files Modified
| File | Changes |
|------|---------|
| `api/app/services/render/svg.py` | Removed beerGrad + amber glow; solid dark bg #1a1a1a; reduced all vinyl stroke widths |
| `api/app/services/render/cricut.py` | Reduced white layer stroke width 0.5 → 0.4 |

## Tests

### Updated Tests
- `test_dark_background`: Checks for `#1a1a1a` instead of `beerGrad`/`#2a1f0e`
- `test_green_interior_amber`: Updated — checks for green stroke presence (glow removed)
- `test_existing_modes_unchanged`: Checks standard mode doesn't have `#1a1a1a`
- `test_render_glass_mode`: Checks for `#1a1a1a` instead of `beerGrad`

### Test Results
- **298 tests passed**, 0 failed, 0 errors
