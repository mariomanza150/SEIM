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

const mockAdminPayload = {
  ...mockPayload,
  global: {
    pending_review_total: 0,
    unassigned_pending_review: 0,
    stale_under_review_14d: 0,
  },
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

  it('shows empty distribution message when admin global section has no rows', async () => {
    api.get.mockResolvedValue({ data: mockAdminPayload })
    const wrapper = mount(CoordinatorWorkload, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Institution overview')
    expect(wrapper.text()).toContain('No assigned pending applications by coordinator.')
  })

  it('shows Spanish empty distribution message', async () => {
    setAppLocale('es')
    api.get.mockResolvedValue({ data: mockAdminPayload })
    const wrapper = mount(CoordinatorWorkload, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('No hay solicitudes pendientes asignadas por coordinador.')
  })
})
