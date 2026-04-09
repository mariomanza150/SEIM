/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import CoordinatorWorkload from './CoordinatorWorkload.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

const mockPayload = {
  you: {
    assigned_pending_review: 2,
    coordinated_programs_pending: 5,
    assigned_with_open_resubmit: 1,
    avg_days_in_queue_assigned: 4.2,
  },
  global: null,
  distribution: [],
}

describe('CoordinatorWorkload', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockResolvedValue({ data: mockPayload })
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('shows translated heading and your workload section', async () => {
    const wrapper = mount(CoordinatorWorkload, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Coordinator workload')
    expect(wrapper.text()).toContain('Your workload')
    expect(wrapper.text()).toContain('Assigned to you')
    expect(wrapper.text()).toContain('Submitted')
    expect(wrapper.text()).toContain('Under review')
  })

  it('shows Spanish subtitle status highlights', async () => {
    setAppLocale('es')
    const wrapper = mount(CoordinatorWorkload, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Enviada')
    expect(wrapper.text()).toContain('En revisión')
  })
})
