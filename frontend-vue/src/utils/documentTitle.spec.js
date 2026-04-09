/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import i18n, { setAppLocale } from '@/i18n'
import { resolveDocumentTitle, syncAppMetaDescription, syncAppSocialMeta } from './documentTitle'

function removeSocialMetas() {
  document.head
    .querySelectorAll('meta[property^="og:"], meta[name^="twitter:"]')
    .forEach((el) => el.remove())
}

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

describe('syncAppSocialMeta', () => {
  beforeEach(() => {
    setAppLocale('en')
    removeSocialMetas()
  })

  afterEach(() => {
    removeSocialMetas()
    setAppLocale('en')
  })

  it('uses socialTitle when tab title is only the product fallback', () => {
    syncAppSocialMeta((k) => i18n.global.t(k), {})
    expect(document.querySelector('meta[property="og:title"]').getAttribute('content')).toBe(
      i18n.global.t('appMeta.socialTitle'),
    )
    expect(document.querySelector('meta[name="twitter:title"]').getAttribute('content')).toBe(
      i18n.global.t('appMeta.socialTitle'),
    )
  })

  it('uses tab title for named routes', () => {
    syncAppSocialMeta((k) => i18n.global.t(k), { name: 'Dashboard' })
    expect(document.querySelector('meta[property="og:title"]').getAttribute('content')).toBe('Dashboard - SEIM')
  })

  it('follows locale for description and og:locale', () => {
    setAppLocale('es')
    syncAppSocialMeta((k) => i18n.global.t(k), {})
    expect(document.querySelector('meta[property="og:description"]').getAttribute('content')).toContain(
      'intercambio',
    )
    expect(document.querySelector('meta[property="og:locale"]').getAttribute('content')).toBe('es_ES')
  })
})
