import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import CricutExportPanel from '../CricutExportPanel.vue'
import { useDesignerStore } from '../../stores/designer'

function mountComponent(visible = true) {
  const pinia = createPinia()
  setActivePinia(pinia)
  return mount(CricutExportPanel, {
    props: { visible },
    global: { plugins: [pinia] },
  })
}

describe('CricutExportPanel', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders when visible', () => {
    const wrapper = mountComponent(true)
    expect(wrapper.text()).toContain('Export for Cricut')
  })

  it('does not render when not visible', () => {
    const wrapper = mountComponent(false)
    expect(wrapper.find('.fixed').exists()).toBe(false)
  })

  it('shows placeholder when no cricut SVGs generated', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('Cricut export not yet generated')
  })

  it('shows layer previews when cricut SVGs are available', async () => {
    const wrapper = mountComponent()
    const store = useDesignerStore()
    store.cricutSvgs = {
      white: '<svg>white</svg>',
      blue: '<svg>blue</svg>',
      green: '<svg>green</svg>',
      tan: '<svg>tan</svg>',
      guide: '<svg>guide</svg>',
    }
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('White Layer')
    expect(wrapper.text()).toContain('Green Layer')
    expect(wrapper.text()).toContain('Tan Layer')
    expect(wrapper.text()).toContain('Placement Guide')
  })

  it('shows scale verification info when SVGs available', async () => {
    const wrapper = mountComponent()
    const store = useDesignerStore()
    store.cricutSvgs = {
      white: '<svg></svg>',
      blue: '<svg></svg>',
      green: '<svg></svg>',
      tan: '<svg></svg>',
      guide: '<svg></svg>',
    }
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('100% scale')
    expect(wrapper.text()).toContain('10mm reference bar')
  })

  it('shows Download All button', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('Download All (ZIP)')
  })

  it('emits close on close button click', async () => {
    const wrapper = mountComponent()
    await wrapper.find('button').trigger('click') // X button is first
    // The close button in footer
    const buttons = wrapper.findAll('button')
    const closeBtn = buttons.find(b => b.text() === 'Close')
    await closeBtn!.trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('shows loading state when generating', async () => {
    const wrapper = mountComponent()
    const store = useDesignerStore()
    store.cricutLoading = true
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Generating Cricut layers')
  })

  it('has Preview buttons for white/green/tan layers', async () => {
    const wrapper = mountComponent()
    const store = useDesignerStore()
    store.cricutSvgs = {
      white: '<svg></svg>',
      blue: '<svg></svg>',
      green: '<svg></svg>',
      tan: '<svg></svg>',
      guide: '<svg></svg>',
    }
    await wrapper.vm.$nextTick()

    const previewButtons = wrapper.findAll('button').filter(b => b.text() === 'Preview')
    expect(previewButtons.length).toBe(4) // white, blue, green, tan (not guide)
  })

  it('shows Blue Layer in panel', async () => {
    const wrapper = mountComponent()
    const store = useDesignerStore()
    store.cricutSvgs = {
      white: '<svg></svg>',
      blue: '<svg></svg>',
      green: '<svg></svg>',
      tan: '<svg></svg>',
      guide: '<svg></svg>',
    }
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Blue Layer')
    expect(wrapper.text()).toContain('Water hazards')
  })

  it('has Download buttons for all 5 layers', async () => {
    const wrapper = mountComponent()
    const store = useDesignerStore()
    store.cricutSvgs = {
      white: '<svg></svg>',
      blue: '<svg></svg>',
      green: '<svg></svg>',
      tan: '<svg></svg>',
      guide: '<svg></svg>',
    }
    await wrapper.vm.$nextTick()

    const downloadButtons = wrapper.findAll('button').filter(b => b.text() === 'Download')
    expect(downloadButtons.length).toBe(5)
  })
})
