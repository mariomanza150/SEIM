/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import SidebarNavList from './SidebarNavList.vue'
import { SIDEBAR_SECTIONS_KEY } from '@/utils/sidebarPrefs'

const sections = [
  {
    key: 'main',
    label: 'Main',
    items: [
      { key: 'dashboard', to: { name: 'Dashboard' }, label: 'Dashboard', iconClass: 'bi bi-house' },
      { key: 'applications', to: { name: 'Applications' }, label: 'Applications', iconClass: 'bi bi-file' },
    ],
  },
  {
    key: 'admin',
    label: 'Administration',
    items: [{ key: 'adminPrograms', to: { name: 'AdminPrograms' }, label: 'Programs', iconClass: 'bi bi-mortarboard' }],
  },
  { key: 'hidden', label: 'Hidden', isVisible: false, items: [{ key: 'x', to: { name: 'Dashboard' }, label: 'X' }] },
]

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: ['Dashboard', 'Applications', 'AdminPrograms'].map((name) => ({
      path: `/${name}`,
      name,
      component: { template: '<div />' },
    })),
  })
}

async function mountList(props = {}, start = 'Dashboard') {
  const router = makeRouter()
  await router.push({ name: start })
  await router.isReady()
  const wrapper = mount(SidebarNavList, {
    props: { sections, ...props },
    global: { plugins: [router] },
  })
  await flushPromises()
  return { wrapper, router }
}

const panel = (w, key) => w.find(`[data-testid="sidebar-section-${key}"]`)
const toggle = (w, key) => w.find(`[data-testid="sidebar-section-toggle-${key}"]`)

describe('SidebarNavList', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('renders accordion toggles for visible labelled sections, expanded by default', async () => {
    const { wrapper } = await mountList()
    expect(toggle(wrapper, 'main').attributes('aria-expanded')).toBe('true')
    expect(toggle(wrapper, 'admin').attributes('aria-controls')).toBe('seim-nav-section-admin')
    expect(toggle(wrapper, 'hidden').exists()).toBe(false)
    expect(panel(wrapper, 'admin').isVisible()).toBe(true)
  })

  it('collapses a section and persists the state in localStorage', async () => {
    const { wrapper } = await mountList()
    await toggle(wrapper, 'admin').trigger('click')
    expect(toggle(wrapper, 'admin').attributes('aria-expanded')).toBe('false')
    expect(panel(wrapper, 'admin').attributes('style')).toContain('display: none')
    expect(JSON.parse(localStorage.getItem(SIDEBAR_SECTIONS_KEY))).toEqual({ admin: true })

    await toggle(wrapper, 'admin').trigger('click')
    expect(JSON.parse(localStorage.getItem(SIDEBAR_SECTIONS_KEY))).toEqual({})
  })

  it('restores collapsed sections from localStorage', async () => {
    localStorage.setItem(SIDEBAR_SECTIONS_KEY, JSON.stringify({ admin: true }))
    const { wrapper } = await mountList()
    expect(toggle(wrapper, 'admin').attributes('aria-expanded')).toBe('false')
    expect(toggle(wrapper, 'main').attributes('aria-expanded')).toBe('true')
  })

  it('ignores corrupt stored state', async () => {
    localStorage.setItem(SIDEBAR_SECTIONS_KEY, '{not json')
    const { wrapper } = await mountList()
    expect(toggle(wrapper, 'admin').attributes('aria-expanded')).toBe('true')
  })

  it('re-opens a collapsed section when navigating to one of its routes', async () => {
    localStorage.setItem(SIDEBAR_SECTIONS_KEY, JSON.stringify({ admin: true }))
    const { wrapper, router } = await mountList()
    expect(toggle(wrapper, 'admin').attributes('aria-expanded')).toBe('false')
    await router.push({ name: 'AdminPrograms' })
    await flushPromises()
    expect(toggle(wrapper, 'admin').attributes('aria-expanded')).toBe('true')
  })

  it('rail mode renders icon-only links with accessible labels and no section toggles', async () => {
    const { wrapper } = await mountList({ rail: true })
    expect(wrapper.find('[data-testid^="sidebar-section-toggle-"]').exists()).toBe(false)
    const links = wrapper.findAll('a')
    expect(links.map((a) => a.attributes('aria-label'))).toEqual(['Dashboard', 'Applications', 'Programs'])
    expect(links[0].text()).toBe('')
  })

  it('collapsible=false renders plain headings', async () => {
    const { wrapper } = await mountList({ collapsible: false })
    expect(wrapper.find('[data-testid^="sidebar-section-toggle-"]').exists()).toBe(false)
    expect(wrapper.text()).toContain('Administration')
  })
})
