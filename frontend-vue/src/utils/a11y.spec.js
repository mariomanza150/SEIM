/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { announceRouteNavigation, focusMainContent, ROUTE_ANNOUNCE_ID } from './a11y'
import i18n, { setAppLocale } from '@/i18n'

function flushRaf() {
  return new Promise((resolve) => {
    requestAnimationFrame(() => resolve())
  })
}

describe('focusMainContent', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('focuses #main-content when present', () => {
    document.body.innerHTML = '<main id="main-content" tabindex="-1"></main>'
    const el = document.getElementById('main-content')
    const spy = vi.spyOn(el, 'focus')
    focusMainContent()
    expect(spy).toHaveBeenCalledWith({ preventScroll: true })
  })

  it('does not throw when landmark is missing', () => {
    expect(() => focusMainContent()).not.toThrow()
  })
})

describe('announceRouteNavigation', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    document.body.innerHTML = `<div id="${ROUTE_ANNOUNCE_ID}"></div>`
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
    document.body.innerHTML = ''
  })

  it('sets polite live region from route name translation', async () => {
    announceRouteNavigation({ name: 'Dashboard', meta: {} })
    await flushRaf()
    expect(document.getElementById(ROUTE_ANNOUNCE_ID).textContent).toBe('Dashboard')
  })

  it('falls back to meta title without suffix when name unknown', async () => {
    announceRouteNavigation({ name: 'UnknownX', meta: { title: 'Custom - SEIM' } })
    await flushRaf()
    expect(document.getElementById(ROUTE_ANNOUNCE_ID).textContent).toBe('Custom')
  })

  it('uses Spanish route label when locale is es', async () => {
    setAppLocale('es')
    announceRouteNavigation({ name: 'NotFound', meta: {} })
    await flushRaf()
    expect(document.getElementById(ROUTE_ANNOUNCE_ID).textContent).toBe('Página no encontrada')
  })
})
