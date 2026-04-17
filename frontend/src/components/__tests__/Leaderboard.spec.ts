import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Leaderboard from '../Leaderboard.vue'
import { useGameStore } from '../../stores/game'

function mountComponent() {
  const pinia = createPinia()
  setActivePinia(pinia)
  const store = useGameStore()
  store.sessionId = 'sess-123'
  store.playerId = 'player-456'
  store.courseName = 'Pebble Beach'
  store.glassCount = 3
  store.holesPerGlass = 6
  // Mock fetch for auto-refresh
  vi.spyOn(globalThis, 'fetch').mockResolvedValue({
    ok: true,
    json: () => Promise.resolve({ players: [] }),
  } as Response)
  return mount(Leaderboard, {
    global: { plugins: [pinia] },
  })
}

describe('Leaderboard', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('renders header', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('Leaderboard')
    expect(wrapper.text()).toContain('Pebble Beach')
  })

  it('shows empty state when no scores', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('No scores yet')
  })

  it('shows players when leaderboard has entries', async () => {
    const wrapper = mountComponent()
    const store = useGameStore()
    store.leaderboard = [
      { player_id: 'p1', player_name: 'Mike', total_score: 70, holes_played: 18, score_to_par: -2, scores_by_hole: [] },
      { player_id: 'p2', player_name: 'Sarah', total_score: 75, holes_played: 18, score_to_par: 3, scores_by_hole: [] },
    ]
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Mike')
    expect(wrapper.text()).toContain('Sarah')
    expect(wrapper.text()).toContain('-2')
    expect(wrapper.text()).toContain('+3')
  })

  it('highlights current player', async () => {
    const wrapper = mountComponent()
    const store = useGameStore()
    store.leaderboard = [
      { player_id: 'player-456', player_name: 'Mike', total_score: 70, holes_played: 18, score_to_par: -2, scores_by_hole: [] },
    ]
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('(you)')
  })

  it('renders back to scorecard button', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('Back to Scorecard')
  })

  it('shows auto-refresh note', async () => {
    const wrapper = mountComponent()
    const store = useGameStore()
    store.leaderboard = [
      { player_id: 'p1', player_name: 'Mike', total_score: 72, holes_played: 18, score_to_par: 0, scores_by_hole: [] },
    ]
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Auto-refreshes every 10 seconds')
  })
})
