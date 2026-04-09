/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import {
  LOCALE_STORAGE_KEY,
  getStoredLocale,
  detectBrowserLocale,
  getInitialLocale,
  setAppLocale,
} from './index.js'
import i18n from './index.js'

describe('i18n locale helpers', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.stubGlobal('navigator', { language: 'en-US' })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    setAppLocale('en')
    localStorage.clear()
  })

  it('getStoredLocale returns null when unset', () => {
    localStorage.removeItem(LOCALE_STORAGE_KEY)
    expect(getStoredLocale()).toBeNull()
  })

  it('getInitialLocale prefers localStorage over browser', () => {
    localStorage.setItem(LOCALE_STORAGE_KEY, 'es')
    expect(getInitialLocale()).toBe('es')
  })

  it('detectBrowserLocale maps Spanish', () => {
    vi.stubGlobal('navigator', { language: 'es-MX' })
    expect(detectBrowserLocale()).toBe('es')
  })

  it('setAppLocale persists and updates active locale', () => {
    setAppLocale('es')
    expect(i18n.global.locale.value).toBe('es')
    expect(localStorage.getItem(LOCALE_STORAGE_KEY)).toBe('es')
    expect(document.documentElement.lang).toBe('es')
  })
})
