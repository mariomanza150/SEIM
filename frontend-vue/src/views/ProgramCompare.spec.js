/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ProgramCompare from './ProgramCompare.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

const mockReplace = vi.fn()
const mockRoute = { query: {} }

vi.mock('vue-router', () => ({
  useRouter: () => ({ replace: mockReplace }),
  useRoute: () => mockRoute,
}))

describe('ProgramCompare', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    mockRoute.query = {}
    api.get.mockResolvedValue({
      data: {
        results: [
          { id: 1, name: 'Alpha Program', start_date: '2025-09-01', end_date: '2025-12-15' },
          { id: 2, name: 'Beta Program', start_date: '2026-01-10', end_date: '2026-05-01' },
        ],
        next: null,
      },
    })
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('shows translated page heading and picker label', async () => {
    const wrapper = mount(ProgramCompare, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Compare programs')
    expect(wrapper.text()).toContain('Programs to compare (0 / 4)')
    expect(wrapper.find('[data-testid="program-compare-hint"]').text()).toContain(
      'Choose at least two programs',
    )
  })
})
