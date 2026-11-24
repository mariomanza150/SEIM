/**
 * @vitest-environment jsdom
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import i18n, { setAppLocale } from '@/i18n'
import { useQaStore } from '@/stores/qa'
import TesterMenu from './TesterMenu.vue'

vi.mock('@/services/api', () => ({ default: { get: vi.fn() } }))

const stubs = { RouterLink: { template: '<a><slot /></a>' } }

describe('TesterMenu', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setAppLocale('en')
  })

  it('is hidden for non-testers', () => {
    const w = mount(TesterMenu, { global: { plugins: [i18n], stubs } })
    expect(w.find('[data-testid="qa-tester-menu"]').exists()).toBe(false)
  })

  it('shows tier badge, version and my reports for testers', async () => {
    const qa = useQaStore()
    qa.context = { enabled: true, is_tester: true, deploy_tier: 'test', version: '1.2.3', commit: 'abcdef123' }
    const w = mount(TesterMenu, { attachTo: document.body, global: { plugins: [i18n], stubs } })
    expect(w.find('[data-testid="qa-tier-badge"]').text()).toBe('TEST')
    const version = w.find('[data-testid="qa-version-badge"]').text()
    expect(version).toContain('v1.2.3')
    expect(w.text()).toContain('My reports')
    expect(w.get('[data-testid="qa-tester-menu-toggle"]').attributes('aria-label')).toBeTruthy()
    const spy = vi.fn()
    window.addEventListener('seim:qa-report', spy)
    await w.find('button.dropdown-item').trigger('click')
    expect(spy).toHaveBeenCalled()
    w.unmount()
  })

  it('closes on Escape via shared nav dropdown behavior', async () => {
    const qa = useQaStore()
    qa.context = { enabled: true, is_tester: true, deploy_tier: 'test' }
    const w = mount(TesterMenu, { attachTo: document.body, global: { plugins: [i18n], stubs } })
    const toggle = w.get('[data-testid="qa-tester-menu-toggle"]')
    await toggle.trigger('click')
    expect(toggle.attributes('aria-expanded')).toBe('true')
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }))
    await w.vm.$nextTick()
    expect(toggle.attributes('aria-expanded')).toBe('false')
    w.unmount()
  })
})
