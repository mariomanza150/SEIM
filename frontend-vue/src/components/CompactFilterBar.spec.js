/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import CompactFilterBar from './CompactFilterBar.vue'
import i18n, { setAppLocale } from '@/i18n'

describe('CompactFilterBar', () => {
  beforeEach(() => {
    setAppLocale('en')
  })

  afterEach(() => {
    setAppLocale('en')
  })

  it('keeps advanced filters and presets collapsed until toggled', async () => {
    const wrapper = mount(CompactFilterBar, {
      props: { testId: 'demo-filters', clearLabel: 'Clear' },
      slots: {
        primary: '<div class="col-md-4"><input data-testid="primary-search" /></div>',
        advanced: '<label>Status extra</label>',
        presets: '<input data-testid="preset-name" placeholder="Preset name" />',
      },
      global: { plugins: [i18n] },
    })

    expect(wrapper.find('[data-testid="demo-filters"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="primary-search"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="compact-filter-extra"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="preset-name"]').exists()).toBe(false)

    await wrapper.get('[data-testid="compact-filter-advanced-toggle"]').trigger('click')
    expect(wrapper.find('[data-testid="compact-filter-extra"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="preset-name"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Advanced filters')
  })

  it('emits clear from the primary row and uses Spanish toggle copy', async () => {
    setAppLocale('es')
    const wrapper = mount(CompactFilterBar, {
      slots: {
        primary: '<div class="col"></div>',
        advanced: '<span>more</span>',
      },
      global: { plugins: [i18n] },
    })

    expect(wrapper.get('[data-testid="compact-filter-clear"]').text()).toContain(
      i18n.global.t('common.clearFilters'),
    )
    expect(wrapper.get('[data-testid="compact-filter-advanced-toggle"]').text()).toContain(
      i18n.global.t('common.advancedFilters'),
    )
    await wrapper.get('[data-testid="compact-filter-clear"]').trigger('click')
    expect(wrapper.emitted('clear')).toHaveLength(1)
  })

  it('hides the disclosure toggle when there is no advanced or presets slot', () => {
    const wrapper = mount(CompactFilterBar, {
      slots: { primary: '<div class="col"></div>' },
      global: { plugins: [i18n] },
    })
    expect(wrapper.find('[data-testid="compact-filter-advanced-toggle"]').exists()).toBe(false)
  })
})
