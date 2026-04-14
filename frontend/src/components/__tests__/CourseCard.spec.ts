import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CourseCard from '../CourseCard.vue'

const baseCourse = {
  id: 1,
  course_name: 'Pebble Beach Golf Links',
  club_name: 'Pebble Beach Resorts',
  locationStr: 'Pebble Beach, CA',
  stats: { par: 72, yards: 6828, rating: 74.7, slope: 145 },
}

describe('CourseCard', () => {
  it('renders course name and club name', () => {
    const wrapper = mount(CourseCard, {
      props: { course: baseCourse, selected: false },
    })
    expect(wrapper.text()).toContain('Pebble Beach Golf Links')
    expect(wrapper.text()).toContain('Pebble Beach Resorts')
  })

  it('hides club name when same as course name', () => {
    const course = { ...baseCourse, club_name: 'Pebble Beach Golf Links' }
    const wrapper = mount(CourseCard, {
      props: { course, selected: false },
    })
    const clubLines = wrapper.findAll('p')
    const clubNameEl = clubLines.find((el) => el.text() === 'Pebble Beach Golf Links' && el.classes().length > 0)
    expect(clubNameEl).toBeUndefined()
  })

  it('renders location string', () => {
    const wrapper = mount(CourseCard, {
      props: { course: baseCourse, selected: false },
    })
    expect(wrapper.text()).toContain('Pebble Beach, CA')
  })

  it('renders stats when present', () => {
    const wrapper = mount(CourseCard, {
      props: { course: baseCourse, selected: false },
    })
    expect(wrapper.text()).toContain('72')
    expect(wrapper.text()).toContain('6,828')
    expect(wrapper.text()).toContain('74.7')
    expect(wrapper.text()).toContain('145')
  })

  it('does not render stats when absent', () => {
    const course = { ...baseCourse, stats: null }
    const wrapper = mount(CourseCard, {
      props: { course, selected: false },
    })
    expect(wrapper.text()).not.toContain('Par')
    expect(wrapper.text()).not.toContain('Rating')
  })

  it('applies selected styling when selected', () => {
    const wrapper = mount(CourseCard, {
      props: { course: baseCourse, selected: true },
    })
    expect(wrapper.find('div').classes()).toContain('bg-emerald-900/50')
  })

  it('applies hover styling when not selected', () => {
    const wrapper = mount(CourseCard, {
      props: { course: baseCourse, selected: false },
    })
    expect(wrapper.find('div').classes()).toContain('hover:bg-gray-800')
  })
})
