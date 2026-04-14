import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import GlassControls from '../GlassControls.vue'
import { useDesignerStore } from '../../stores/designer'

function mountComponent() {
  const pinia = createPinia()
  setActivePinia(pinia)
  return mount(GlassControls, {
    global: { plugins: [pinia] },
  })
}

describe('GlassControls', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders glass count buttons', () => {
    const wrapper = mountComponent()
    const buttons = wrapper.findAll('button')
    const glassButtons = buttons.filter((b) => ['1', '2', '3', '6'].includes(b.text()))
    expect(glassButtons.length).toBe(4)
  })

  it('clicking glass count button updates store', async () => {
    const wrapper = mountComponent()
    const store = useDesignerStore()
    expect(store.glassCount).toBe(3)

    const btn6 = wrapper.findAll('button').find((b) => b.text() === '6')
    await btn6!.trigger('click')
    expect(store.glassCount).toBe(6)
  })

  it('renders dimension inputs with defaults', () => {
    const wrapper = mountComponent()
    const inputs = wrapper.findAll('input[type="number"]')
    expect(inputs.length).toBeGreaterThanOrEqual(5)
  })

  it('renders fill mode select', () => {
    const wrapper = mountComponent()
    const selects = wrapper.findAll('select')
    const fillSelect = selects.find((s) => s.text().includes('Full glass'))
    expect(fillSelect).toBeTruthy()
  })

  it('renders preview mode buttons including vinyl, scoring and cricut', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('Vinyl')
    expect(wrapper.text()).toContain('Glass')
    expect(wrapper.text()).toContain('Rect')
    expect(wrapper.text()).toContain('Scoring')
    expect(wrapper.text()).toContain('C-White')
    expect(wrapper.text()).toContain('C-Green')
    expect(wrapper.text()).toContain('C-Tan')
  })

  it('vinyl button is the first preview mode button', () => {
    const wrapper = mountComponent()
    const previewButtons = wrapper.findAll('button').filter((b) =>
      ['Vinyl', 'Glass', 'Rect', 'Scoring', 'C-White', 'C-Green', 'C-Tan'].includes(b.text())
    )
    expect(previewButtons[0].text()).toBe('Vinyl')
  })

  it('clicking Vinyl button sets store mode to vinyl-preview', async () => {
    const wrapper = mountComponent()
    const store = useDesignerStore()
    store.previewMode = 'glass'

    const vinylBtn = wrapper.findAll('button').find((b) => b.text() === 'Vinyl')
    await vinylBtn!.trigger('click')
    expect(store.previewMode).toBe('vinyl-preview')
  })

  it('renders font selector', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('Arial')
    expect(wrapper.text()).toContain('Oswald')
  })

  it('renders show text checkbox', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('Show text labels')
  })

  it('renders color code holes checkbox', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('Color code holes')
  })
})
