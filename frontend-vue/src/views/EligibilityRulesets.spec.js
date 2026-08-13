/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import EligibilityRulesets from './EligibilityRulesets.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}))

describe('EligibilityRulesets', () => {
  beforeEach(() => {
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockResolvedValue({
      data: {
        results: [{ id: 'rs-1', name: 'Default', is_active: true, updated_at: '2026-04-01T00:00:00Z', rules_json: {} }],
      },
    })
  })

  it('lists rulesets for staff', async () => {
    const wrapper = mount(EligibilityRulesets, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' }, PageHeader: { template: '<div><slot /><slot name="actions" /></div>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="eligibility-rulesets-page"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Default')
  })

  it('opens create editor', async () => {
    const wrapper = mount(EligibilityRulesets, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' }, PageHeader: { template: '<div><slot /><slot name="actions" /></div>' } },
      },
    })
    await flushPromises()
    await wrapper.find('[data-testid="ruleset-create"]').trigger('click')
    expect(wrapper.find('[data-testid="ruleset-editor"]').exists()).toBe(true)
  })
})
