/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Applications from './Applications.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), delete: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

describe('Applications', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    global.confirm = vi.fn(() => false)
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('shows translated empty state when list is empty', async () => {
    api.get.mockResolvedValue({ data: { results: [], count: 0, next: null, previous: null } })
    const wrapper = mount(Applications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('No applications yet')
    expect(wrapper.text()).toContain('My applications')
  })

  it('renders draft card with translated labels', async () => {
    api.get.mockResolvedValue({
      data: {
        results: [
          {
            id: '1',
            status: 'draft',
            created_at: '2026-01-10T12:00:00Z',
            program: { name: 'Test Program', institution: 'Uni' },
          },
        ],
        count: 1,
        next: null,
        previous: null,
      },
    })
    const wrapper = mount(Applications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Test Program')
    expect(wrapper.text()).toContain('Draft')
    expect(wrapper.text()).toContain('View details')
    expect(wrapper.find('[data-testid="application-detail-link"]').exists()).toBe(true)
  })
})
