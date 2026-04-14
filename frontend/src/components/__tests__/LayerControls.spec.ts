import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LayerControls from '../LayerControls.vue'
import { useDesignerStore, ALL_LAYERS } from '../../stores/designer'

function mountComponent() {
  const pinia = createPinia()
  setActivePinia(pinia)
  return mount(LayerControls, {
    global: { plugins: [pinia] },
  })
}

describe('LayerControls', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders all layer toggles including ruler', () => {
    const wrapper = mountComponent()
    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    expect(checkboxes.length).toBe(ALL_LAYERS.length)
  })

  it('renders layer labels', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('Fairway')
    expect(wrapper.text()).toContain('Green')
    expect(wrapper.text()).toContain('Bunker')
    expect(wrapper.text()).toContain('Water')
  })

  it('background checkbox is unchecked by default', () => {
    const wrapper = mountComponent()
    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    // background is first layer and hidden by default
    const bgCheckbox = checkboxes[0]
    expect((bgCheckbox.element as HTMLInputElement).checked).toBe(false)
  })

  it('toggling checkbox updates store', async () => {
    const wrapper = mountComponent()
    const store = useDesignerStore()
    expect(store.hiddenLayers.has('fairway')).toBe(false)

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    // fairway is index 2 in ALL_LAYERS
    const fairwayIdx = ALL_LAYERS.indexOf('fairway')
    await checkboxes[fairwayIdx].trigger('change')

    expect(store.hiddenLayers.has('fairway')).toBe(true)
  })

  it('renders color picker inputs for visible layers', () => {
    const wrapper = mountComponent()
    const colorInputs = wrapper.findAll('input[type="color"]')
    // Each visible layer has 2 color pickers (fill + stroke)
    // 8 visible layers (all except background and ruler) × 2 = 16
    expect(colorInputs.length).toBeGreaterThanOrEqual(16)
  })

  it('renders stroke width inputs', () => {
    const wrapper = mountComponent()
    const numberInputs = wrapper.findAll('input[type="number"]')
    expect(numberInputs.length).toBeGreaterThanOrEqual(8) // one per visible layer
  })

  it('includes ruler layer toggle', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('Ruler')
  })
})
