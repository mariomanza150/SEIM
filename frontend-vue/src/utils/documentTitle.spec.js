/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import i18n, { setAppLocale } from '@/i18n'
import { resolveDocumentTitle } from './documentTitle'

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
