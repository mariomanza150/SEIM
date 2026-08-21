/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ScholarshipScoringRulesets from './ScholarshipScoringRulesets.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}))

const sampleRow = {
  id: 'ssr-1',
  slug: 'default_v1',
  label: 'Default scholarship rubric (v1)',
  is_active: true,
  updated_at: '2026-04-01T00:00:00Z',
  factor_weights: {
    academic: 25,
    language: 20,
    program_fit: 15,
    application_quality: 25,
    timeliness: 15,
  },
}

describe('ScholarshipScoringRulesets', () => {
  beforeEach(() => {
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockResolvedValue({ data: { results: [sampleRow] } })
  })

  it('lists rulesets for staff', async () => {
    const wrapper = mount(ScholarshipScoringRulesets, {
      global: {
        plugins: [i18n],
        stubs: {
          RouterLink: { template: '<a><slot /></a>' },
          PageHeader: { template: '<div><slot /><slot name="actions" /></div>' },
        },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="scholarship-scoring-rulesets-page"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Default scholarship rubric (v1)')
    expect(wrapper.get('[data-testid="scholarship-ruleset-slug"]').text()).toBe('default_v1')
  })

  it('opens editor with factor weight inputs', async () => {
    const wrapper = mount(ScholarshipScoringRulesets, {
      global: {
        plugins: [i18n],
        stubs: {
          RouterLink: { template: '<a><slot /></a>' },
          PageHeader: { template: '<div><slot /><slot name="actions" /></div>' },
        },
      },
    })
    await flushPromises()
    await wrapper.find('[data-testid="scholarship-ruleset-edit"]').trigger('click')
    expect(wrapper.find('[data-testid="scholarship-ruleset-editor"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="scholarship-weight-academic"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="scholarship-ruleset-mvp-note"]').exists()).toBe(true)
  })

  it('patches factor weights on save', async () => {
    api.patch.mockResolvedValue({ data: { ...sampleRow, factor_weights: { ...sampleRow.factor_weights, academic: 30 } } })
    const wrapper = mount(ScholarshipScoringRulesets, {
      global: {
        plugins: [i18n],
        stubs: {
          RouterLink: { template: '<a><slot /></a>' },
          PageHeader: { template: '<div><slot /><slot name="actions" /></div>' },
        },
      },
    })
    await flushPromises()
    await wrapper.find('[data-testid="scholarship-ruleset-edit"]').trigger('click')
    await wrapper.find('[data-testid="scholarship-weight-academic"]').setValue(30)
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()
    expect(api.patch).toHaveBeenCalled()
    const [url, payload] = api.patch.mock.calls[0]
    expect(url).toContain('/api/scholarship-scoring-rulesets/ssr-1/')
    expect(payload.factor_weights.academic).toBe(30)
    expect(payload.slug).toBeUndefined()
  })

  it('localizes chrome in Spanish', async () => {
    setAppLocale('es')
    const wrapper = mount(ScholarshipScoringRulesets, {
      global: {
        plugins: [i18n],
        stubs: {
          RouterLink: { template: '<a><slot /></a>' },
          PageHeader: {
            props: ['title'],
            template: '<div><h1>{{ title }}</h1><slot name="actions" /><slot /></div>',
          },
        },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toMatch(/Rúbrica de puntuación de becas/i)
    expect(wrapper.find('[data-testid="scholarship-ruleset-create"]').text()).toMatch(/Nuevo conjunto/i)
  })
})
