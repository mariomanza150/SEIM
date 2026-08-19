/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Nominations from './Nominations.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), put: vi.fn(), post: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

describe('Nominations', () => {
  beforeEach(() => {
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockImplementation((url) => {
      if (url === '/api/programs/') {
        return Promise.resolve({ data: { results: [{ id: 'prog-1', name: 'Erasmus Berlin' }] } })
      }
      if (String(url).includes('/nominations/')) {
        return Promise.resolve({
          data: {
            program_id: 'prog-1',
            enrollment_capacity: 1,
            slots_remaining: 1,
            applications: [
              {
                id: 'app-1',
                student_display_name: 'Ada L.',
                status: 'submitted',
                nomination_rank: 1,
                submitted_at: '2026-08-07T05:23:31.065839+00:00',
              },
            ],
          },
        })
      }
      return Promise.reject(new Error(url))
    })
  })

  it('loads ranked applicants and matches seats', async () => {
    api.post.mockResolvedValue({
      data: {
        applications: [
          { id: 'app-1', student_display_name: 'Ada L.', status: 'nominated', nomination_rank: 1 },
        ],
        matched: { nominated: 1, waitlisted: 0 },
      },
    })
    const wrapper = mount(Nominations, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' }, PageHeader: { template: '<div><slot /></div>' } },
      },
    })
    await flushPromises()
    await wrapper.find('[data-testid="nominations-program"]').setValue('prog-1')
    await flushPromises()
    expect(wrapper.find('[data-testid="nominations-table"]').text()).toContain('Ada L.')
    expect(wrapper.find('[data-testid="nomination-submitted-at"]').text()).not.toContain('2026-08-07T')
    expect(wrapper.find('[data-testid="nomination-submitted-at"]').text()).not.toBe('—')
    await wrapper.find('[data-testid="nominations-match"]').trigger('click')
    await flushPromises()
    expect(api.post).toHaveBeenCalledWith('/api/programs/prog-1/nominations/match/')
    expect(wrapper.text()).toContain('nominated')
  })
})
