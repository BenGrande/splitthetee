import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SvgPreview from '../SvgPreview.vue'

describe('SvgPreview', () => {
  it('shows empty message when no SVG content', () => {
    const wrapper = mount(SvgPreview, {
      props: { svgContent: '', loading: false },
    })
    expect(wrapper.text()).toContain('Search and select a course to begin')
  })

  it('renders SVG content when provided', () => {
    const wrapper = mount(SvgPreview, {
      props: {
        svgContent: '<svg><rect width="100" height="100" fill="red"/></svg>',
        loading: false,
      },
    })
    expect(wrapper.html()).toContain('<rect')
  })

  it('shows loading overlay when loading', () => {
    const wrapper = mount(SvgPreview, {
      props: { svgContent: '<svg></svg>', loading: true },
    })
    expect(wrapper.text()).toContain('Rendering...')
  })

  it('hides loading overlay when not loading', () => {
    const wrapper = mount(SvgPreview, {
      props: { svgContent: '<svg></svg>', loading: false },
    })
    expect(wrapper.text()).not.toContain('Rendering...')
  })

  it('exposes resetZoom method', () => {
    const wrapper = mount(SvgPreview, {
      props: { svgContent: '', loading: false },
    })
    expect(typeof wrapper.vm.resetZoom).toBe('function')
  })
})
