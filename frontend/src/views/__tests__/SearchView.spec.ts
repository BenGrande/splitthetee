import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import SearchView from '../SearchView.vue'
import { useCourseStore } from '../../stores/course'

function createTestRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'search', component: SearchView },
      { path: '/designer', name: 'designer', component: { template: '<div />' } },
    ],
  })
}

function mountSearchView() {
  const pinia = createPinia()
  setActivePinia(pinia)
  const router = createTestRouter()
  return mount(SearchView, {
    global: {
      plugins: [pinia, router],
    },
  })
}

describe('SearchView', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('renders the header with app title', () => {
    const wrapper = mountSearchView()
    expect(wrapper.text()).toContain('One Nine')
  })

  it('renders the search input', () => {
    const wrapper = mountSearchView()
    const input = wrapper.find('input[type="text"]')
    expect(input.exists()).toBe(true)
    expect(input.attributes('placeholder')).toContain('Search golf courses')
  })

  it('shows empty state before searching', () => {
    const wrapper = mountSearchView()
    expect(wrapper.text()).toContain('Search for a golf course to get started')
  })

  it('calls store.search on form submit', async () => {
    const wrapper = mountSearchView()
    const store = useCourseStore()
    store.search = vi.fn()

    await wrapper.find('input').setValue('pebble beach')
    await wrapper.find('form').trigger('submit')

    expect(store.search).toHaveBeenCalledWith('pebble beach')
  })

  it('does not search with empty query', async () => {
    const wrapper = mountSearchView()
    const store = useCourseStore()
    store.search = vi.fn()

    await wrapper.find('form').trigger('submit')

    expect(store.search).not.toHaveBeenCalled()
  })

  it('displays course cards when results exist', async () => {
    const wrapper = mountSearchView()
    const store = useCourseStore()

    store.courses = [
      {
        id: 1,
        course_name: 'Pebble Beach',
        club_name: 'Pebble Beach',
        location: { city: 'Pebble Beach', state: 'CA', country: 'United States' },
        tees: { male: [{ par_total: 72, total_yards: 6828, course_rating: 74.7, slope_rating: 145, number_of_holes: 18, tee_name: 'Blue' }] },
      },
    ]

    // Trigger hasSearched
    store.search = vi.fn()
    await wrapper.find('input').setValue('pebble')
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Pebble Beach')
    expect(wrapper.text()).toContain('1 course found')
  })

  it('shows "no courses found" for empty results after searching', async () => {
    const wrapper = mountSearchView()
    const store = useCourseStore()
    store.search = vi.fn()
    store.courses = []

    await wrapper.find('input').setValue('zzzzzzz')
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('No courses found')
  })

  it('shows select a course placeholder when no course selected', () => {
    const wrapper = mountSearchView()
    expect(wrapper.text()).toContain('Select a course')
  })

  it('shows course details when a course is selected', async () => {
    const wrapper = mountSearchView()
    const store = useCourseStore()

    store.selectedCourse = {
      id: 1,
      course_name: 'Augusta National',
      club_name: 'Augusta National Golf Club',
      location: { city: 'Augusta', state: 'GA', latitude: 33.5, longitude: -82.0 },
    }
    store.courses = [
      {
        ...store.selectedCourse,
        tees: { male: [{ par_total: 72, total_yards: 7475, course_rating: 78.1, slope_rating: 148, number_of_holes: 18, tee_name: 'Championship' }] },
      },
    ]
    store.courseData = {
      holes: [
        { number: 1, par: 4, yards: 445, handicap: 4 },
        { number: 2, par: 5, yards: 575, handicap: 13 },
      ],
    }

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Augusta National')
    expect(wrapper.text()).toContain('Augusta National Golf Club')
    expect(wrapper.text()).toContain('Hole Details')
  })

  it('renders hole table with correct data', async () => {
    const wrapper = mountSearchView()
    const store = useCourseStore()

    store.selectedCourse = {
      id: 1,
      course_name: 'Test Course',
      club_name: 'Test Club',
      location: { city: 'Test', state: 'TS' },
    }
    store.courseData = {
      holes: [{ number: 1, par: 4, yards: 400, handicap: 7 }],
    }

    await wrapper.vm.$nextTick()

    const table = wrapper.find('table')
    expect(table.exists()).toBe(true)
    expect(table.text()).toContain('400')
    expect(table.text()).toContain('7')
  })

  it('has an Open Designer button when course is selected', async () => {
    const wrapper = mountSearchView()
    const store = useCourseStore()

    store.selectedCourse = {
      id: 1,
      course_name: 'Test',
      club_name: 'Test',
      location: { city: 'X', state: 'Y', latitude: 1, longitude: 2 },
    }
    store.courseData = { holes: [] }

    await wrapper.vm.$nextTick()

    const designerBtn = wrapper.findAll('button').find((b) => b.text() === 'Open Designer')
    expect(designerBtn?.exists()).toBe(true)
  })
})
