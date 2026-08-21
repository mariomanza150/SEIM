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
        results: [
          {
            id: 'rs-1',
            name: 'Default',
            is_active: true,
            schema_version: 2,
            content_revision: 3,
            updated_at: '2026-04-01T00:00:00Z',
            rules_json: {},
          },
        ],
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
    expect(wrapper.get('[data-testid="ruleset-schema-version"]').text()).toContain('v2')
    expect(wrapper.get('[data-testid="ruleset-content-revision"]').text()).toContain('r3')
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

  it('saves with document schema_version 2', async () => {
    api.post.mockResolvedValue({ data: { id: 'rs-2' } })
    const wrapper = mount(EligibilityRulesets, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' }, PageHeader: { template: '<div><slot /><slot name="actions" /></div>' } },
      },
    })
    await flushPromises()
    await wrapper.find('[data-testid="ruleset-create"]').trigger('click')
    await wrapper.find('[data-testid="ruleset-name"]').setValue('Strict')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()
    expect(api.post).toHaveBeenCalled()
    const payload = api.post.mock.calls[0][1]
    expect(payload.schema_version).toBe(2)
    expect(payload.rules_json).toEqual({ program_overrides: {} })
  })
})
