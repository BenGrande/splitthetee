# Task 007: Add Vinyl Preview Mode to Designer UI

## Priority: HIGH
## Depends on: 006 (complete), API Task 009
## Phase: Post-Phase 5 enhancement

## Summary
Add `vinyl-preview` as a new preview mode in the designer, make it the default, and add a toolbar button for it.

## Files to Modify

### `frontend/src/stores/designer.ts`
1. Add `'vinyl-preview'` to the `previewMode` type/union (currently has `'rect'`, `'glass'`, `'scoring-preview'`, and cricut modes)
2. Change the default `previewMode` value from whatever it is now to `'vinyl-preview'`
3. Ensure `renderGlass()` action sends `mode: 'vinyl-preview'` to the API when this mode is selected

### `frontend/src/components/GlassControls.vue`
1. Add a "Vinyl" button to the preview mode button group (alongside Rect, Glass, Scoring, Cricut modes)
2. Position it as the FIRST button (since it's the default)
3. Style: use a distinctive style — perhaps a glass/crystal icon or just "Vinyl" text with an outline style
4. Keyboard shortcut: `v` key for vinyl-preview (add to existing keyboard shortcut handler alongside g/r/s)

### `frontend/src/views/DesignerView.vue`
1. If the mode toolbar is here instead of GlassControls, add the Vinyl button here
2. Ensure the vinyl-preview mode triggers a re-render via the store

## Visual Notes
- The vinyl-preview SVG from the API will have a dark background, so the preview area should NOT add its own dark background (or should use a neutral/transparent checker pattern)
- The SVG preview component (`SvgPreview.vue`) may need a minor tweak: if the current background is white/light, consider making it transparent or a subtle checker pattern so the dark SVG background shows correctly

## Tests
- Test that designer store initializes with `previewMode: 'vinyl-preview'`
- Test that the Vinyl button exists in the mode toolbar
- Test that clicking Vinyl sets the store mode to `'vinyl-preview'`
- Test that `v` keyboard shortcut switches to vinyl-preview
- Test that render payload includes `mode: 'vinyl-preview'`

## Definition of Done
- [ ] `vinyl-preview` is a valid preview mode in the designer store
- [ ] It is the DEFAULT mode on page load
- [ ] Vinyl button appears in the mode toolbar as the first option
- [ ] Keyboard shortcut `v` works
- [ ] Render API call uses `mode: 'vinyl-preview'` when selected
- [ ] SVG preview area displays the dark-background vinyl SVG correctly
- [ ] All existing tests pass
- [ ] New tests pass
