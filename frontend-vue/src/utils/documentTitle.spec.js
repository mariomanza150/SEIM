/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import i18n, { setAppLocale } from '@/i18n'
import { resolveDocumentTitle, syncAppMetaDescription } from './documentTitle'

describe('resolveDocumentTitle', () => {
  beforeEach(() => {
    setAppLocale('en')
  })

  afterEach(() => {
    setAppLocale('en')
  })

  it('uses route name and fallback product title in English', () => {
    expect(resolveDocumentTitle({ name: 'Dashboard' })).toBe('Dashboard - SEIM')
  })

  it('uses Spanish route names when locale is es', () => {
    setAppLocale('es')
    expect(resolveDocumentTitle({ name: 'Dashboard' })).toBe('Panel - SEIM')
  })

  it('uses localized 404 tab title for NotFound', () => {
    expect(resolveDocumentTitle({ name: 'NotFound' })).toBe('404 — Page not found - SEIM')
    setAppLocale('es')
    expect(resolveDocumentTitle({ name: 'NotFound' })).toBe('404 — Página no encontrada - SEIM')
  })

  it('falls back to product name when name is missing or unknown', () => {
    expect(resolveDocumentTitle({})).toBe('SEIM')
    expect(resolveDocumentTitle({ name: 'UnknownRoute' })).toBe('SEIM')
  })
})

describe('syncAppMetaDescription', () => {
  let meta

  beforeEach(() => {
    meta = document.createElement('meta')
    meta.setAttribute('name', 'description')
    meta.setAttribute('content', 'initial')
    document.head.appendChild(meta)
    setAppLocale('en')
  })

  afterEach(() => {
    if (meta.parentNode) meta.remove()
    setAppLocale('en')
  })

  it('sets meta content from i18n and follows locale', () => {
    syncAppMetaDescription((k) => i18n.global.t(k))
    expect(meta.getAttribute('content')).toContain('Student Exchange')
    setAppLocale('es')
    syncAppMetaDescription((k) => i18n.global.t(k))
    expect(meta.getAttribute('content')).toContain('intercambio')
  })

  it('no-ops when description meta is absent', () => {
    meta.remove()
    expect(() => syncAppMetaDescription((k) => i18n.global.t(k))).not.toThrow()
  })
})
