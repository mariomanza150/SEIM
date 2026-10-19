/**
 * @vitest-environment jsdom
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import api from '@/services/api'
import en from '@/locales/en.json'
import TesterEligibilityOverview from './TesterEligibilityOverview.vue'

vi.mock('@/services/api', () => ({ default: { get: vi.fn() } }))

const i18n = () => createI18n({ legacy: false, locale: 'en', messages: { en } })

function mockApi({ tester }) {
  api.get.mockImplementation((url) => {
    if (url === '/api/qa/context/') {
      return Promise.resolve({ data: { enabled: true, is_tester: tester } })
    }
    if (url === '/api/programs/eligibility-overview/') {
      return Promise.resolve({
        data: {
          results: [
            { id: '1', name: 'Open one', is_active: true, listed: true, blocking: [] },
            {
              id: '2',
              name: 'English one',
              is_active: true,
              listed: false,
              blocking: [
                {
                  id: 'required_language',
                  message: 'raw',
                  message_key: 'language_unmet',
                  message_params: { required: 'English', student: 'Spanish' },
                },
              ],
            },
            {
              id: '3',
              name: 'Off one',
              is_active: false,
              listed: false,
              blocking: [{ id: 'is_active', message: 'Program is not active.', message_key: 'program_inactive', message_params: {} }],
            },
          ],
        },
      })
    }
    return Promise.reject(new Error(`unexpected ${url}`))
  })
}

describe('TesterEligibilityOverview', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('lists hidden programs with translated reasons for testers', async () => {
    mockApi({ tester: true })
    const wrapper = mount(TesterEligibilityOverview, { global: { plugins: [i18n()] } })
    await flushPromises()
    const rows = wrapper.findAll('[data-testid="tester-eligibility-row"]')
    expect(rows).toHaveLength(2)
    expect(rows[0].text()).toContain('English one')
    expect(rows[0].text()).toContain('Language requirement not met. Required: English, Your language: Spanish')
    expect(rows[1].text()).toContain(en.eligibilityRules.program_inactive)
    expect(wrapper.text()).not.toContain('Open one')
  })

  it('renders nothing and skips the endpoint for non-testers', async () => {
    mockApi({ tester: false })
    const wrapper = mount(TesterEligibilityOverview, { global: { plugins: [i18n()] } })
    await flushPromises()
    expect(wrapper.find('[data-testid="tester-eligibility-overview"]').exists()).toBe(false)
    expect(api.get).not.toHaveBeenCalledWith('/api/programs/eligibility-overview/')
  })
})
